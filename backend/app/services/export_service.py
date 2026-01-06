"""
Export service for CSV and JSON data export.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import csv
import io
import json

from ..models.workout import Workout, ComputedMetricsModel
from ..models.domain import DomainScoreModel


class ExportService:
    """Service for data export operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_csv(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export workouts as CSV."""
        workouts = self._get_workouts(user_id, start_date, end_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            "workout_id",
            "name",
            "workout_type",
            "template_type",
            "performed_at",
            "total_time_seconds",
            "round_count",
            "total_ewu",
            "density_power_min",
            "density_power_sec",
            "active_power",
            "repeatability_drift",
            "repeatability_spread",
            "repeatability_consistency",
            "lift_ewu",
            "machine_ewu",
            "gymnastics_ewu",
            "lift_share",
            "machine_share",
            "gymnastics_share",
            "notes"
        ])
        
        # Data rows
        for workout in workouts:
            metrics = workout.metrics
            writer.writerow([
                workout.id,
                workout.name or "",
                workout.workout_type or "",
                workout.template_type,
                workout.performed_at.isoformat(),
                workout.total_time_seconds,
                workout.round_count,
                metrics.total_ewu if metrics else "",
                metrics.density_power_min if metrics else "",
                metrics.density_power_sec if metrics else "",
                metrics.active_power if metrics else "",
                metrics.repeatability_drift if metrics else "",
                metrics.repeatability_spread if metrics else "",
                metrics.repeatability_consistency if metrics else "",
                metrics.lift_ewu if metrics else "",
                metrics.machine_ewu if metrics else "",
                metrics.gymnastics_ewu if metrics else "",
                metrics.lift_share if metrics else "",
                metrics.machine_share if metrics else "",
                metrics.gymnastics_share if metrics else "",
                workout.notes or ""
            ])
        
        return output.getvalue()
    
    def export_json(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_distributions: bool = False
    ) -> dict:
        """Export workouts as JSON."""
        workouts = self._get_workouts(user_id, start_date, end_date)
        domain_scores = self._get_domain_scores(user_id)
        
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "workout_count": len(workouts),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "workouts": [],
            "domain_scores": []
        }
        
        # Add workouts
        for workout in workouts:
            workout_data = {
                "id": workout.id,
                "name": workout.name,
                "workout_type": workout.workout_type,
                "template_type": workout.template_type,
                "performed_at": workout.performed_at.isoformat(),
                "total_time_seconds": workout.total_time_seconds,
                "round_count": workout.round_count,
                "notes": workout.notes,
                "movements": [
                    {
                        "movement_type": m.movement_type,
                        "modality": m.modality,
                        "reps": m.reps,
                        "load_lb": m.load_lb,
                        "calories": m.calories,
                        "order_index": m.order_index
                    }
                    for m in sorted(workout.movements, key=lambda x: x.order_index)
                ],
                "splits": [
                    {
                        "round_number": s.round_number,
                        "time_seconds": s.time_seconds
                    }
                    for s in sorted(workout.splits, key=lambda x: x.round_number)
                ],
                "metrics": None
            }
            
            if workout.metrics:
                metrics = workout.metrics
                workout_data["metrics"] = {
                    "total_ewu": metrics.total_ewu,
                    "density_power_min": metrics.density_power_min,
                    "density_power_sec": metrics.density_power_sec,
                    "active_power": metrics.active_power,
                    "repeatability": {
                        "drift": metrics.repeatability_drift,
                        "spread": metrics.repeatability_spread,
                        "consistency": metrics.repeatability_consistency
                    } if metrics.repeatability_drift is not None else None,
                    "lift_ewu": metrics.lift_ewu,
                    "machine_ewu": metrics.machine_ewu,
                    "gymnastics_ewu": metrics.gymnastics_ewu,
                    "lift_share": metrics.lift_share,
                    "machine_share": metrics.machine_share,
                    "gymnastics_share": metrics.gymnastics_share,
                    "per_round_power": metrics.per_round_power,
                    "total_active_seconds": metrics.total_active_seconds,
                    "rest_seconds": metrics.rest_seconds,
                    "computed_at": metrics.computed_at.isoformat() if metrics.computed_at else None
                }
            
            export_data["workouts"].append(workout_data)
        
        # Add domain scores
        for score in domain_scores:
            export_data["domain_scores"].append({
                "domain": score.domain,
                "raw_value": score.raw_value,
                "normalized_score": score.normalized_score,
                "sample_count": score.sample_count,
                "confidence": score.confidence,
                "updated_at": score.updated_at.isoformat() if score.updated_at else None
            })
        
        return export_data
    
    def _get_workouts(
        self,
        user_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Workout]:
        """Get workouts with optional date filter."""
        query = self.db.query(Workout).filter(Workout.user_id == user_id)
        
        if start_date:
            query = query.filter(Workout.performed_at >= start_date)
        
        if end_date:
            query = query.filter(Workout.performed_at <= end_date)
        
        return query.order_by(Workout.performed_at.desc()).all()
    
    def _get_domain_scores(self, user_id: str) -> List[DomainScoreModel]:
        """Get domain scores for user."""
        return self.db.query(DomainScoreModel).filter(
            DomainScoreModel.user_id == user_id
        ).all()
