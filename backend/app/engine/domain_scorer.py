"""
Domain Scorer

Updates Athlete Completeness domain scores based on workout metrics.

Domains:
1. Strength Output - Updated by lift-heavy workouts (total lift EWU)
2. Monostructural Output - Updated by mono workouts (total machine EWU)
3. Mixed-Modal Capacity - Updated by density power from mixed workouts
4. Sprint/Power Capacity - ONLY from sub-5min tests (density power in sprints)
5. Repeatability - Updated by drift/spread metrics when splits available

CRITICAL: Each workout ONLY updates domains it has evidence for.
Do NOT fabricate scores when data is missing - display "no data".
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from .normalizer import (
    ConfidenceLevel, 
    get_confidence_level,
    normalize_value,
    Distribution,
    DistributionStore,
    add_to_distribution
)
from .metrics_calculator import ComputedMetrics
from .workout_typer import WorkoutType


class DomainType(str, Enum):
    STRENGTH_OUTPUT = "strength_output"
    MONOSTRUCTURAL_OUTPUT = "monostructural_output"
    MIXED_MODAL_CAPACITY = "mixed_modal_capacity"
    SPRINT_POWER_CAPACITY = "sprint_power_capacity"
    REPEATABILITY = "repeatability"


# Domain metric mappings
# Each domain uses a primary metric for scoring
DOMAIN_PRIMARY_METRIC: Dict[DomainType, str] = {
    DomainType.STRENGTH_OUTPUT: "lift_ewu",
    DomainType.MONOSTRUCTURAL_OUTPUT: "machine_ewu",
    DomainType.MIXED_MODAL_CAPACITY: "density_power_min",
    DomainType.SPRINT_POWER_CAPACITY: "sprint_density_power",
    DomainType.REPEATABILITY: "repeatability_consistency",
}

# Whether higher values are better for each domain
DOMAIN_POLARITY: Dict[DomainType, bool] = {
    DomainType.STRENGTH_OUTPUT: True,
    DomainType.MONOSTRUCTURAL_OUTPUT: True,
    DomainType.MIXED_MODAL_CAPACITY: True,
    DomainType.SPRINT_POWER_CAPACITY: True,
    DomainType.REPEATABILITY: True,  # Consistency (higher = better)
}


@dataclass
class DomainScore:
    """Score for a single domain."""
    domain: DomainType
    raw_value: Optional[float]
    normalized_score: Optional[float]  # 0-100
    sample_count: int
    confidence: ConfidenceLevel
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def has_data(self) -> bool:
        return self.sample_count > 0
    
    def to_dict(self) -> dict:
        return {
            "domain": self.domain.value,
            "raw_value": self.raw_value,
            "normalized_score": self.normalized_score,
            "sample_count": self.sample_count,
            "confidence": self.confidence.value,
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class AthleteCompleteness:
    """Complete radar chart data for an athlete."""
    user_id: str
    domains: Dict[DomainType, DomainScore]
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_radar_data(self) -> List[dict]:
        """Convert to radar chart format."""
        return [
            {
                "domain": domain.value,
                "label": self._get_label(domain),
                "score": score.normalized_score,
                "confidence": score.confidence.value,
                "has_data": score.has_data
            }
            for domain, score in self.domains.items()
        ]
    
    @staticmethod
    def _get_label(domain: DomainType) -> str:
        labels = {
            DomainType.STRENGTH_OUTPUT: "Strength",
            DomainType.MONOSTRUCTURAL_OUTPUT: "Monostructural",
            DomainType.MIXED_MODAL_CAPACITY: "Mixed-Modal",
            DomainType.SPRINT_POWER_CAPACITY: "Sprint/Power",
            DomainType.REPEATABILITY: "Repeatability",
        }
        return labels.get(domain, domain.value)


def get_qualifying_domains(
    workout_type: WorkoutType,
    metrics: ComputedMetrics
) -> List[DomainType]:
    """
    Determine which domains a workout qualifies to update.
    
    IMPORTANT: Only return domains where we have actual evidence.
    """
    domains = []
    
    # Strength Output: Must have significant lift component
    if metrics.lift_ewu > 0 and metrics.lift_share >= 0.3:
        domains.append(DomainType.STRENGTH_OUTPUT)
    
    # Monostructural Output: Only from monostructural workouts
    if workout_type == WorkoutType.MONOSTRUCTURAL:
        domains.append(DomainType.MONOSTRUCTURAL_OUTPUT)
    
    # Mixed-Modal Capacity: Any workout with mixed modalities
    if metrics.lift_share > 0 and metrics.machine_share > 0:
        domains.append(DomainType.MIXED_MODAL_CAPACITY)
    
    # Sprint/Power Capacity: ONLY from sprint workouts
    if workout_type == WorkoutType.SPRINT:
        domains.append(DomainType.SPRINT_POWER_CAPACITY)
    
    # Repeatability: Only when we have repeatability metrics
    if metrics.repeatability is not None and metrics.repeatability.consistency is not None:
        domains.append(DomainType.REPEATABILITY)
    
    return domains


def extract_domain_metric(
    domain: DomainType,
    metrics: ComputedMetrics
) -> Optional[float]:
    """Extract the primary metric value for a domain."""
    if domain == DomainType.STRENGTH_OUTPUT:
        return metrics.lift_ewu if metrics.lift_ewu > 0 else None
    
    elif domain == DomainType.MONOSTRUCTURAL_OUTPUT:
        return metrics.machine_ewu if metrics.machine_ewu > 0 else None
    
    elif domain == DomainType.MIXED_MODAL_CAPACITY:
        return metrics.density_power_per_min if metrics.density_power_per_min > 0 else None
    
    elif domain == DomainType.SPRINT_POWER_CAPACITY:
        return metrics.density_power_per_min if metrics.density_power_per_min > 0 else None
    
    elif domain == DomainType.REPEATABILITY:
        if metrics.repeatability and metrics.repeatability.consistency is not None:
            return metrics.repeatability.consistency
        return None
    
    return None


class DomainScoreManager:
    """
    Manages domain scores for athletes.
    
    Responsibilities:
    1. Determine which domains to update for a workout
    2. Update distributions with new metric values
    3. Recalculate normalized scores
    4. Track confidence levels
    """
    
    def __init__(self, distribution_store: DistributionStore):
        self.distribution_store = distribution_store
        self._domain_scores: Dict[str, Dict[DomainType, DomainScore]] = {}
    
    def _get_user_scores(self, user_id: str) -> Dict[DomainType, DomainScore]:
        """Get or create domain scores for a user."""
        if user_id not in self._domain_scores:
            # Initialize with empty scores for all domains
            self._domain_scores[user_id] = {
                domain: DomainScore(
                    domain=domain,
                    raw_value=None,
                    normalized_score=None,
                    sample_count=0,
                    confidence=ConfidenceLevel.NO_DATA
                )
                for domain in DomainType
            }
        return self._domain_scores[user_id]
    
    def update_from_workout(
        self,
        user_id: str,
        workout_id: str,
        workout_type: WorkoutType,
        metrics: ComputedMetrics,
        performed_at: datetime
    ) -> List[DomainType]:
        """
        Update domain scores based on a new workout.
        
        Returns: List of domains that were updated
        """
        # Get qualifying domains
        qualifying_domains = get_qualifying_domains(workout_type, metrics)
        
        updated_domains = []
        user_scores = self._get_user_scores(user_id)
        
        for domain in qualifying_domains:
            # Extract the metric value for this domain
            metric_value = extract_domain_metric(domain, metrics)
            
            if metric_value is None:
                continue
            
            # Get or create distribution for this domain
            metric_name = DOMAIN_PRIMARY_METRIC[domain]
            distribution = self.distribution_store.get_or_create(
                user_id=user_id,
                workout_type=workout_type.value,
                metric_name=metric_name
            )
            
            # Add value to distribution
            distribution = add_to_distribution(
                distribution=distribution,
                value=metric_value,
                workout_id=workout_id,
                performed_at=performed_at
            )
            self.distribution_store.save(distribution)
            
            # Normalize the value
            higher_is_better = DOMAIN_POLARITY[domain]
            normalized = normalize_value(metric_value, distribution, higher_is_better)
            
            # Update domain score
            user_scores[domain] = DomainScore(
                domain=domain,
                raw_value=metric_value,
                normalized_score=normalized.normalized_score,
                sample_count=normalized.sample_count,
                confidence=normalized.confidence,
                updated_at=datetime.now()
            )
            
            updated_domains.append(domain)
        
        return updated_domains
    
    def get_athlete_completeness(self, user_id: str) -> AthleteCompleteness:
        """Get the complete radar chart data for an athlete."""
        user_scores = self._get_user_scores(user_id)
        
        return AthleteCompleteness(
            user_id=user_id,
            domains=user_scores,
            last_updated=datetime.now()
        )
    
    def get_domain_detail(
        self,
        user_id: str,
        domain: DomainType
    ) -> Dict:
        """Get detailed breakdown for a specific domain."""
        user_scores = self._get_user_scores(user_id)
        domain_score = user_scores.get(domain)
        
        if not domain_score:
            return {
                "domain": domain.value,
                "has_data": False,
                "message": "No data available for this domain"
            }
        
        return {
            "domain": domain.value,
            "raw_value": domain_score.raw_value,
            "normalized_score": domain_score.normalized_score,
            "sample_count": domain_score.sample_count,
            "confidence": domain_score.confidence.value,
            "has_data": domain_score.has_data,
            "updated_at": domain_score.updated_at.isoformat()
        }


# Example usage
if __name__ == "__main__":
    from .ewu_calculator import MovementData, MovementType, calculate_workout_ewu
    from .metrics_calculator import SplitData, calculate_metrics
    from .workout_typer import classify_workout
    
    # Set up stores
    dist_store = DistributionStore()
    scorer = DomainScoreManager(dist_store)
    
    user_id = "user-123"
    
    # Simulate several workouts to build up data
    print("=== Building Domain Scores ===\n")
    
    # Workout 1: Interval workout (our sample)
    movements = [
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
        MovementData(MovementType.POWER_SNATCH, reps=8, load_lb=95),
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
    ]
    splits = [
        SplitData(1, 90), SplitData(2, 88), SplitData(3, 89),
        SplitData(4, 89), SplitData(5, 96), SplitData(6, 94),
    ]
    
    workout_ewu = calculate_workout_ewu(movements, round_count=6)
    total_time = 18 * 60 + 14
    metrics = calculate_metrics(workout_ewu, total_time, splits)
    workout_type_result = classify_workout(
        movements, workout_ewu, total_time, 6, True
    )
    
    updated = scorer.update_from_workout(
        user_id=user_id,
        workout_id="workout-1",
        workout_type=workout_type_result.workout_type,
        metrics=metrics,
        performed_at=datetime.now()
    )
    
    print(f"Workout 1 (Interval): Updated domains: {[d.value for d in updated]}")
    
    # Workout 2: Sprint test
    sprint_movements = [
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=25),
    ]
    sprint_ewu = calculate_workout_ewu(sprint_movements, round_count=1)
    sprint_metrics = calculate_metrics(sprint_ewu, 180, None)  # 3 min
    
    updated = scorer.update_from_workout(
        user_id=user_id,
        workout_id="workout-2",
        workout_type=WorkoutType.SPRINT,
        metrics=sprint_metrics,
        performed_at=datetime.now()
    )
    
    print(f"Workout 2 (Sprint): Updated domains: {[d.value for d in updated]}")
    
    # Get final radar data
    completeness = scorer.get_athlete_completeness(user_id)
    
    print(f"\n=== Athlete Completeness Radar ===")
    for item in completeness.to_radar_data():
        score_str = f"{item['score']:.1f}" if item['score'] is not None else "N/A"
        print(f"  {item['label']}: {score_str}/100 ({item['confidence']})")
