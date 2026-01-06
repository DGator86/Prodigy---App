"""
Workout service for CRUD and metric computation.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import json

from ..models.workout import Workout, Movement, Split, ComputedMetricsModel
from ..models.domain import DomainScoreModel, DistributionModel
from ..schemas.workout import (
    WorkoutCreate,
    WorkoutUpdate,
    MovementInput,
    SplitInput,
    MetricsResponse,
    RepeatabilityResponse,
    ActivePowerResponse,
)
from ..engine import (
    MovementData,
    MovementType,
    SplitData,
    WorkoutType,
    TemplateType,
    calculate_workout_ewu,
    calculate_metrics,
    classify_workout,
    get_modality,
    DomainType,
    get_qualifying_domains,
    extract_domain_metric,
    ConfidenceLevel,
    get_confidence_level,
    calculate_percentile,
)


class WorkoutService:
    """Service for workout operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_workout(
        self,
        user_id: str,
        workout_data: WorkoutCreate
    ) -> Tuple[Workout, MetricsResponse, List[str]]:
        """
        Create a new workout with computed metrics.
        
        Returns:
            Tuple of (Workout, MetricsResponse, list of updated domain names)
        """
        # Convert movements to engine format
        engine_movements = [
            MovementData(
                movement_type=MovementType(m.movement_type.value),
                reps=m.reps,
                load_lb=m.load_lb,
                calories=m.calories,
            )
            for m in workout_data.movements
        ]
        
        # Calculate EWU
        workout_ewu = calculate_workout_ewu(
            movements=engine_movements,
            round_count=workout_data.round_count
        )
        
        # Convert splits to engine format
        engine_splits = None
        if workout_data.splits:
            engine_splits = [
                SplitData(
                    round_number=s.round_number,
                    time_seconds=s.time_seconds
                )
                for s in workout_data.splits
            ]
        
        # Calculate metrics
        computed_metrics = calculate_metrics(
            workout_ewu=workout_ewu,
            total_time_seconds=workout_data.total_time_seconds,
            splits=engine_splits
        )
        
        # Classify workout type
        template_type = TemplateType(workout_data.template_type.value)
        type_result = classify_workout(
            movements=engine_movements,
            workout_ewu=workout_ewu,
            total_time_seconds=workout_data.total_time_seconds,
            round_count=workout_data.round_count,
            has_splits=bool(workout_data.splits),
            template_type=template_type
        )
        
        # Create workout record
        workout = Workout(
            user_id=user_id,
            name=workout_data.name,
            workout_type=type_result.workout_type.value,
            template_type=workout_data.template_type.value,
            total_time_seconds=workout_data.total_time_seconds,
            round_count=workout_data.round_count,
            notes=workout_data.notes,
            performed_at=workout_data.performed_at,
        )
        self.db.add(workout)
        self.db.flush()  # Get workout ID
        
        # Create movement records
        for m in workout_data.movements:
            modality = get_modality(MovementType(m.movement_type.value))
            movement = Movement(
                workout_id=workout.id,
                movement_type=m.movement_type.value,
                modality=modality.value,
                load_lb=m.load_lb,
                reps=m.reps,
                calories=m.calories,
                order_index=m.order_index,
            )
            self.db.add(movement)
        
        # Create split records
        if workout_data.splits:
            for s in workout_data.splits:
                split = Split(
                    workout_id=workout.id,
                    round_number=s.round_number,
                    time_seconds=s.time_seconds,
                )
                self.db.add(split)
        
        # Create computed metrics record
        metrics_record = ComputedMetricsModel(
            workout_id=workout.id,
            total_ewu=computed_metrics.total_ewu,
            density_power_min=computed_metrics.density_power_per_min,
            density_power_sec=computed_metrics.density_power_per_sec,
            active_power=computed_metrics.active_power.average_active_power if computed_metrics.active_power else None,
            repeatability_drift=computed_metrics.repeatability.drift if computed_metrics.repeatability else None,
            repeatability_spread=computed_metrics.repeatability.spread if computed_metrics.repeatability else None,
            repeatability_consistency=computed_metrics.repeatability.consistency if computed_metrics.repeatability else None,
            lift_ewu=computed_metrics.lift_ewu,
            machine_ewu=computed_metrics.machine_ewu,
            gymnastics_ewu=computed_metrics.gymnastics_ewu,
            lift_share=computed_metrics.lift_share,
            machine_share=computed_metrics.machine_share,
            gymnastics_share=computed_metrics.gymnastics_share,
            total_active_seconds=computed_metrics.total_active_seconds,
            rest_seconds=computed_metrics.rest_seconds,
            per_round_power=computed_metrics.active_power.per_round_power if computed_metrics.active_power else None,
        )
        self.db.add(metrics_record)
        
        # Update domain scores
        updated_domains = self._update_domain_scores(
            user_id=user_id,
            workout_id=workout.id,
            workout_type=type_result.workout_type,
            metrics=computed_metrics,
            performed_at=workout_data.performed_at
        )
        
        self.db.commit()
        self.db.refresh(workout)
        
        # Build metrics response
        metrics_response = self._build_metrics_response(computed_metrics)
        
        return workout, metrics_response, updated_domains
    
    def _update_domain_scores(
        self,
        user_id: str,
        workout_id: str,
        workout_type: WorkoutType,
        metrics,
        performed_at: datetime
    ) -> List[str]:
        """Update domain scores based on workout metrics."""
        updated_domains = []
        
        # Get qualifying domains
        qualifying_domains = get_qualifying_domains(workout_type, metrics)
        
        for domain in qualifying_domains:
            domain_name = domain.value
            metric_value = extract_domain_metric(domain, metrics)
            
            if metric_value is None:
                continue
            
            # Update distribution
            self._update_distribution(
                user_id=user_id,
                workout_type=workout_type.value,
                metric_name=domain_name,
                value=metric_value,
                workout_id=workout_id,
                performed_at=performed_at
            )
            
            # Get updated distribution for normalization
            dist = self._get_distribution(user_id, workout_type.value, domain_name)
            values = [v["value"] for v in dist.values_json] if dist else []
            
            # Calculate normalized score
            normalized_score = None
            if values:
                percentile = calculate_percentile(metric_value, sorted(values))
                normalized_score = percentile * 100
            
            sample_count = len(values)
            confidence = get_confidence_level(sample_count).value
            
            # Update or create domain score
            domain_score = self.db.query(DomainScoreModel).filter(
                DomainScoreModel.user_id == user_id,
                DomainScoreModel.domain == domain_name
            ).first()
            
            if domain_score:
                domain_score.raw_value = metric_value
                domain_score.normalized_score = normalized_score
                domain_score.sample_count = sample_count
                domain_score.confidence = confidence
            else:
                domain_score = DomainScoreModel(
                    user_id=user_id,
                    domain=domain_name,
                    raw_value=metric_value,
                    normalized_score=normalized_score,
                    sample_count=sample_count,
                    confidence=confidence
                )
                self.db.add(domain_score)
            
            updated_domains.append(domain_name)
        
        return updated_domains
    
    def _update_distribution(
        self,
        user_id: str,
        workout_type: str,
        metric_name: str,
        value: float,
        workout_id: str,
        performed_at: datetime
    ) -> None:
        """Update distribution with new value."""
        dist = self._get_distribution(user_id, workout_type, metric_name)
        
        if dist:
            # Prune old values (180 day window)
            cutoff = datetime.utcnow() - timedelta(days=180)
            values = [
                v for v in dist.values_json
                if datetime.fromisoformat(v["performed_at"]) >= cutoff
            ]
            
            # Add new value
            values.append({
                "value": value,
                "workout_id": workout_id,
                "performed_at": performed_at.isoformat()
            })
            
            dist.values_json = values
        else:
            # Create new distribution
            dist = DistributionModel(
                user_id=user_id,
                workout_type=workout_type,
                metric_name=metric_name,
                values_json=[{
                    "value": value,
                    "workout_id": workout_id,
                    "performed_at": performed_at.isoformat()
                }]
            )
            self.db.add(dist)
    
    def _get_distribution(
        self,
        user_id: str,
        workout_type: str,
        metric_name: str
    ) -> Optional[DistributionModel]:
        """Get distribution for user/workout_type/metric."""
        return self.db.query(DistributionModel).filter(
            DistributionModel.user_id == user_id,
            DistributionModel.workout_type == workout_type,
            DistributionModel.metric_name == metric_name
        ).first()
    
    def _build_metrics_response(self, computed_metrics) -> MetricsResponse:
        """Build metrics response from computed metrics."""
        repeatability = None
        if computed_metrics.repeatability:
            repeatability = RepeatabilityResponse(
                drift=computed_metrics.repeatability.drift,
                spread=computed_metrics.repeatability.spread,
                consistency=computed_metrics.repeatability.consistency,
                first_half_avg=computed_metrics.repeatability.first_half_avg,
                second_half_avg=computed_metrics.repeatability.second_half_avg,
                best_bout_time=computed_metrics.repeatability.best_bout_time,
                worst_bout_time=computed_metrics.repeatability.worst_bout_time,
            )
        
        active_power = None
        if computed_metrics.active_power:
            active_power = ActivePowerResponse(
                average_active_power=computed_metrics.active_power.average_active_power,
                per_round_power=computed_metrics.active_power.per_round_power,
                peak_power=computed_metrics.active_power.peak_power,
                lowest_power=computed_metrics.active_power.lowest_power,
            )
        
        return MetricsResponse(
            total_ewu=computed_metrics.total_ewu,
            density_power_min=computed_metrics.density_power_per_min,
            density_power_sec=computed_metrics.density_power_per_sec,
            active_power=active_power,
            repeatability=repeatability,
            lift_ewu=computed_metrics.lift_ewu,
            machine_ewu=computed_metrics.machine_ewu,
            gymnastics_ewu=computed_metrics.gymnastics_ewu,
            lift_share=computed_metrics.lift_share,
            machine_share=computed_metrics.machine_share,
            gymnastics_share=computed_metrics.gymnastics_share,
            total_time_seconds=computed_metrics.total_time_seconds,
            total_active_seconds=computed_metrics.total_active_seconds,
            rest_seconds=computed_metrics.rest_seconds,
        )
    
    def get_workout(self, user_id: str, workout_id: str) -> Optional[Workout]:
        """Get a specific workout for user."""
        return self.db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user_id
        ).first()
    
    def get_workouts(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        workout_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Workout], int]:
        """Get paginated workouts for user."""
        query = self.db.query(Workout).filter(Workout.user_id == user_id)
        
        if workout_type:
            query = query.filter(Workout.workout_type == workout_type)
        
        if start_date:
            query = query.filter(Workout.performed_at >= start_date)
        
        if end_date:
            query = query.filter(Workout.performed_at <= end_date)
        
        total = query.count()
        
        workouts = query.order_by(desc(Workout.performed_at))\
            .offset((page - 1) * limit)\
            .limit(limit)\
            .all()
        
        return workouts, total
    
    def delete_workout(self, user_id: str, workout_id: str) -> bool:
        """Delete a workout."""
        workout = self.get_workout(user_id, workout_id)
        if not workout:
            return False
        
        self.db.delete(workout)
        self.db.commit()
        return True
    
    def get_domain_scores(self, user_id: str) -> List[DomainScoreModel]:
        """Get all domain scores for user."""
        # Get existing scores
        existing = self.db.query(DomainScoreModel).filter(
            DomainScoreModel.user_id == user_id
        ).all()
        
        # Create dict for easy lookup
        scores_dict = {s.domain: s for s in existing}
        
        # Ensure all domains have entries
        all_domains = [
            "strength_output",
            "monostructural_output",
            "mixed_modal_capacity",
            "sprint_power_capacity",
            "repeatability"
        ]
        
        result = []
        for domain in all_domains:
            if domain in scores_dict:
                result.append(scores_dict[domain])
            else:
                # Create placeholder with no data
                placeholder = DomainScoreModel(
                    user_id=user_id,
                    domain=domain,
                    raw_value=None,
                    normalized_score=None,
                    sample_count=0,
                    confidence="no_data"
                )
                result.append(placeholder)
        
        return result
    
    def get_trends(
        self,
        user_id: str,
        period: str = "30d"
    ) -> dict:
        """Get trend data for user."""
        # Parse period
        days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get workouts in period
        workouts = self.db.query(Workout).filter(
            Workout.user_id == user_id,
            Workout.performed_at >= cutoff
        ).order_by(Workout.performed_at).all()
        
        # Build trend data
        density_data = []
        repeatability_data = []
        ewu_data = []
        
        for w in workouts:
            if w.metrics:
                density_data.append({
                    "date": w.performed_at.isoformat(),
                    "value": w.metrics.density_power_min
                })
                
                if w.metrics.repeatability_consistency is not None:
                    repeatability_data.append({
                        "date": w.performed_at.isoformat(),
                        "value": w.metrics.repeatability_consistency
                    })
                
                ewu_data.append({
                    "date": w.performed_at.isoformat(),
                    "value": w.metrics.total_ewu
                })
        
        return {
            "period": period,
            "density_power": {
                "data": density_data,
                "average": sum(d["value"] for d in density_data) / len(density_data) if density_data else None
            },
            "repeatability": {
                "data": repeatability_data,
                "average": sum(d["value"] for d in repeatability_data) / len(repeatability_data) if repeatability_data else None
            },
            "total_ewu": {
                "data": ewu_data,
                "sum": sum(d["value"] for d in ewu_data) if ewu_data else 0
            }
        }
