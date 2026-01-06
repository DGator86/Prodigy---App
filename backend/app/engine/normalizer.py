"""
Normalizer

Converts raw metrics to normalized 0-100 scores via percentile ranking.

Process:
1. Maintain rolling distributions per (user, workout_type, metric)
2. When new metric comes in, calculate percentile rank
3. Convert to 0-100 score
4. Handle edge cases (not enough data, provisional scores)

Confidence Levels:
- no_data: sample_count == 0
- low: sample_count < 5
- medium: 5 <= sample_count < 15
- high: sample_count >= 15
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import bisect


class ConfidenceLevel(str, Enum):
    NO_DATA = "no_data"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Confidence thresholds
LOW_THRESHOLD = 5
MEDIUM_THRESHOLD = 15

# Default rolling window
DEFAULT_WINDOW_DAYS = 180


@dataclass
class DistributionValue:
    """A single value in a distribution."""
    value: float
    workout_id: str
    performed_at: datetime


@dataclass
class Distribution:
    """Distribution of values for a specific metric."""
    user_id: str
    workout_type: str
    metric_name: str
    values: List[DistributionValue] = field(default_factory=list)
    window_days: int = DEFAULT_WINDOW_DAYS
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "workout_type": self.workout_type,
            "metric_name": self.metric_name,
            "values": [
                {
                    "value": v.value,
                    "workout_id": v.workout_id,
                    "performed_at": v.performed_at.isoformat()
                }
                for v in self.values
            ],
            "window_days": self.window_days,
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Distribution":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            workout_type=data["workout_type"],
            metric_name=data["metric_name"],
            values=[
                DistributionValue(
                    value=v["value"],
                    workout_id=v["workout_id"],
                    performed_at=datetime.fromisoformat(v["performed_at"])
                )
                for v in data.get("values", [])
            ],
            window_days=data.get("window_days", DEFAULT_WINDOW_DAYS),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


@dataclass
class NormalizedScore:
    """Result of normalizing a metric value."""
    raw_value: float
    normalized_score: Optional[float]  # 0-100, None if no data
    percentile: Optional[float]        # 0-1, None if no data
    sample_count: int
    confidence: ConfidenceLevel
    is_provisional: bool               # True if confidence is low


def get_confidence_level(sample_count: int) -> ConfidenceLevel:
    """Determine confidence level based on sample count."""
    if sample_count == 0:
        return ConfidenceLevel.NO_DATA
    elif sample_count < LOW_THRESHOLD:
        return ConfidenceLevel.LOW
    elif sample_count < MEDIUM_THRESHOLD:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.HIGH


def calculate_percentile(value: float, sorted_values: List[float]) -> float:
    """
    Calculate the percentile rank of a value within a distribution.
    
    Uses linear interpolation for values between existing points.
    Returns value between 0.0 and 1.0.
    """
    if not sorted_values:
        return 0.5  # Default to median if no data
    
    n = len(sorted_values)
    
    if n == 1:
        # Single value - compare to it
        if value < sorted_values[0]:
            return 0.25
        elif value > sorted_values[0]:
            return 0.75
        else:
            return 0.5
    
    # Find position in sorted list
    pos = bisect.bisect_left(sorted_values, value)
    
    if pos == 0:
        # Below all values
        return 0.0
    elif pos == n:
        # Above all values
        return 1.0
    else:
        # Between two values - calculate percentile
        # Number of values strictly less than this value
        lower = sum(1 for v in sorted_values if v < value)
        # Number of values equal to this value
        equal = sum(1 for v in sorted_values if v == value)
        
        # Percentile = (lower + 0.5 * equal) / n
        percentile = (lower + 0.5 * equal) / n
        return percentile


def prune_distribution(
    distribution: Distribution,
    cutoff_date: Optional[datetime] = None
) -> Distribution:
    """
    Remove values outside the rolling window.
    
    Args:
        distribution: The distribution to prune
        cutoff_date: Custom cutoff date (default: now - window_days)
        
    Returns:
        Distribution with old values removed
    """
    if cutoff_date is None:
        cutoff_date = datetime.now() - timedelta(days=distribution.window_days)
    
    distribution.values = [
        v for v in distribution.values
        if v.performed_at >= cutoff_date
    ]
    distribution.updated_at = datetime.now()
    
    return distribution


def add_to_distribution(
    distribution: Distribution,
    value: float,
    workout_id: str,
    performed_at: datetime
) -> Distribution:
    """
    Add a new value to the distribution.
    
    1. Prunes old values outside window
    2. Adds new value
    3. Updates timestamp
    """
    # Prune old values
    distribution = prune_distribution(distribution)
    
    # Add new value
    distribution.values.append(DistributionValue(
        value=value,
        workout_id=workout_id,
        performed_at=performed_at
    ))
    distribution.updated_at = datetime.now()
    
    return distribution


def normalize_value(
    value: float,
    distribution: Distribution,
    higher_is_better: bool = True
) -> NormalizedScore:
    """
    Normalize a value using the distribution.
    
    Args:
        value: The raw metric value
        distribution: The distribution to compare against
        higher_is_better: If True, higher values get higher scores.
                         If False (e.g., drift), lower is better.
    
    Returns:
        NormalizedScore with percentile and 0-100 score
    """
    sample_count = len(distribution.values)
    confidence = get_confidence_level(sample_count)
    
    if sample_count == 0:
        return NormalizedScore(
            raw_value=value,
            normalized_score=None,
            percentile=None,
            sample_count=0,
            confidence=ConfidenceLevel.NO_DATA,
            is_provisional=True
        )
    
    # Get sorted values for percentile calculation
    sorted_values = sorted(v.value for v in distribution.values)
    
    # Calculate percentile
    percentile = calculate_percentile(value, sorted_values)
    
    # Convert to 0-100 score
    if higher_is_better:
        normalized_score = percentile * 100
    else:
        # For metrics where lower is better (e.g., drift, spread)
        normalized_score = (1 - percentile) * 100
    
    return NormalizedScore(
        raw_value=value,
        normalized_score=round(normalized_score, 2),
        percentile=round(percentile, 4),
        sample_count=sample_count,
        confidence=confidence,
        is_provisional=confidence in [ConfidenceLevel.NO_DATA, ConfidenceLevel.LOW]
    )


# Metric configuration: which metrics are "higher is better"
METRIC_POLARITY: Dict[str, bool] = {
    "total_ewu": True,
    "density_power_min": True,
    "density_power_sec": True,
    "active_power": True,
    "repeatability_drift": False,    # Lower drift is better
    "repeatability_spread": False,   # Lower spread is better
    "repeatability_consistency": True,  # Higher consistency is better
    "lift_ewu": True,
    "machine_ewu": True,
}


def normalize_metrics(
    metrics: Dict[str, float],
    distributions: Dict[str, Distribution]
) -> Dict[str, NormalizedScore]:
    """
    Normalize multiple metrics at once.
    
    Args:
        metrics: Dict of metric_name -> raw_value
        distributions: Dict of metric_name -> Distribution
        
    Returns:
        Dict of metric_name -> NormalizedScore
    """
    results = {}
    
    for metric_name, value in metrics.items():
        if value is None:
            continue
            
        distribution = distributions.get(metric_name)
        
        if distribution is None:
            # No distribution yet
            results[metric_name] = NormalizedScore(
                raw_value=value,
                normalized_score=None,
                percentile=None,
                sample_count=0,
                confidence=ConfidenceLevel.NO_DATA,
                is_provisional=True
            )
        else:
            higher_is_better = METRIC_POLARITY.get(metric_name, True)
            results[metric_name] = normalize_value(value, distribution, higher_is_better)
    
    return results


class DistributionStore:
    """
    In-memory store for distributions (for testing).
    In production, this would be backed by database.
    """
    
    def __init__(self):
        self._distributions: Dict[str, Distribution] = {}
    
    def _make_key(self, user_id: str, workout_type: str, metric_name: str) -> str:
        return f"{user_id}:{workout_type}:{metric_name}"
    
    def get(
        self,
        user_id: str,
        workout_type: str,
        metric_name: str
    ) -> Optional[Distribution]:
        """Get a distribution."""
        key = self._make_key(user_id, workout_type, metric_name)
        return self._distributions.get(key)
    
    def get_or_create(
        self,
        user_id: str,
        workout_type: str,
        metric_name: str
    ) -> Distribution:
        """Get or create a distribution."""
        key = self._make_key(user_id, workout_type, metric_name)
        
        if key not in self._distributions:
            self._distributions[key] = Distribution(
                user_id=user_id,
                workout_type=workout_type,
                metric_name=metric_name
            )
        
        return self._distributions[key]
    
    def save(self, distribution: Distribution) -> None:
        """Save a distribution."""
        key = self._make_key(
            distribution.user_id,
            distribution.workout_type,
            distribution.metric_name
        )
        self._distributions[key] = distribution
    
    def get_all_for_user(self, user_id: str) -> List[Distribution]:
        """Get all distributions for a user."""
        return [
            d for d in self._distributions.values()
            if d.user_id == user_id
        ]


# Example usage
if __name__ == "__main__":
    # Simulate building up distributions over time
    store = DistributionStore()
    user_id = "user-123"
    workout_type = "interval"
    
    # Add some historical density power values
    historical_values = [
        (9.5, "w1", datetime(2024, 1, 1)),
        (10.2, "w2", datetime(2024, 1, 5)),
        (10.8, "w3", datetime(2024, 1, 10)),
        (11.1, "w4", datetime(2024, 1, 15)),
        (10.5, "w5", datetime(2024, 1, 20)),
        (11.3, "w6", datetime(2024, 1, 25)),
        (10.9, "w7", datetime(2024, 2, 1)),
        (11.5, "w8", datetime(2024, 2, 5)),
    ]
    
    dist = store.get_or_create(user_id, workout_type, "density_power_min")
    
    for value, wid, date in historical_values:
        dist = add_to_distribution(dist, value, wid, date)
    
    store.save(dist)
    
    # Now normalize a new value
    new_value = 11.58  # From our sample workout
    
    result = normalize_value(new_value, dist, higher_is_better=True)
    
    print("=== Normalization Example ===")
    print(f"\nDistribution ({len(dist.values)} values):")
    sorted_vals = sorted(v.value for v in dist.values)
    print(f"  Range: {min(sorted_vals):.2f} - {max(sorted_vals):.2f}")
    print(f"  Values: {sorted_vals}")
    
    print(f"\nNormalizing new value: {new_value}")
    print(f"  Percentile: {result.percentile:.1%}")
    print(f"  Normalized Score: {result.normalized_score:.1f}/100")
    print(f"  Sample Count: {result.sample_count}")
    print(f"  Confidence: {result.confidence.value}")
    print(f"  Provisional: {result.is_provisional}")
