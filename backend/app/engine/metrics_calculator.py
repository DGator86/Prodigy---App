"""
Metrics Calculator

Computes derived performance metrics from EWU values and split times.

Metrics:
- Total EWU: Sum of all work units
- Density Power: Total_EWU / Total_Time (EWU/min and EWU/s)
- Active Power: Round_EWU / Bout_Time (if splits provided)
- Repeatability:
  - Drift: (avg_second_half - avg_first_half) / avg_first_half (lower is better)
  - Spread: (max_bout - min_bout) / avg_bout (lower is better)
- Modality Share: lift_ewu / total_ewu, machine_ewu / total_ewu
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from statistics import mean, stdev
from .ewu_calculator import WorkoutEWU


@dataclass
class SplitData:
    """Time data for a single round/bout."""
    round_number: int
    time_seconds: float


@dataclass
class RepeatabilityMetrics:
    """Repeatability analysis metrics."""
    drift: Optional[float]       # (second_half_avg - first_half_avg) / first_half_avg
    spread: Optional[float]      # (max - min) / avg
    consistency: Optional[float] # 1 - (stdev / mean), higher is better
    first_half_avg: Optional[float]
    second_half_avg: Optional[float]
    best_bout_time: Optional[float]
    worst_bout_time: Optional[float]


@dataclass
class ActivePowerMetrics:
    """Active power metrics per round."""
    average_active_power: float  # EWU/min during active time
    per_round_power: List[float] # Power for each round
    peak_power: float
    lowest_power: float


@dataclass
class ComputedMetrics:
    """Complete computed metrics for a workout."""
    # Core metrics
    total_ewu: float
    density_power_per_min: float
    density_power_per_sec: float
    
    # Optional metrics (require splits)
    active_power: Optional[ActivePowerMetrics]
    repeatability: Optional[RepeatabilityMetrics]
    
    # Modality breakdown
    lift_ewu: float
    machine_ewu: float
    gymnastics_ewu: float
    lift_share: float
    machine_share: float
    gymnastics_share: float
    
    # Timing
    total_time_seconds: int
    total_active_seconds: Optional[float]  # Sum of splits
    rest_seconds: Optional[float]          # Total - Active


def calculate_density_power(total_ewu: float, total_time_seconds: int) -> Tuple[float, float]:
    """
    Calculate density power (work rate over total session time).
    
    Returns: (ewu_per_minute, ewu_per_second)
    """
    if total_time_seconds <= 0:
        return (0.0, 0.0)
    
    total_minutes = total_time_seconds / 60.0
    
    ewu_per_min = total_ewu / total_minutes
    ewu_per_sec = total_ewu / total_time_seconds
    
    return (round(ewu_per_min, 4), round(ewu_per_sec, 6))


def calculate_active_power(
    round_ewu: float,
    splits: List[SplitData]
) -> Optional[ActivePowerMetrics]:
    """
    Calculate active power (work rate during active bout time only).
    
    Active Power = Round_EWU / Bout_Time (per round)
    Average Active Power = mean of all round powers
    """
    if not splits or len(splits) == 0:
        return None
    
    per_round_power = []
    
    for split in splits:
        if split.time_seconds > 0:
            # Convert to EWU per minute
            bout_minutes = split.time_seconds / 60.0
            power = round_ewu / bout_minutes
            per_round_power.append(round(power, 4))
        else:
            per_round_power.append(0.0)
    
    if not per_round_power:
        return None
    
    return ActivePowerMetrics(
        average_active_power=round(mean(per_round_power), 4),
        per_round_power=per_round_power,
        peak_power=max(per_round_power),
        lowest_power=min(per_round_power)
    )


def calculate_repeatability(splits: List[SplitData]) -> Optional[RepeatabilityMetrics]:
    """
    Calculate repeatability metrics.
    
    Drift: How much slower the athlete gets (second half vs first half)
           Negative drift = getting faster (good)
           Positive drift = slowing down (expected in hard efforts)
           
    Spread: Variance between best and worst bouts
            Lower = more consistent
            
    Consistency: 1 - (stdev / mean)
                 Higher = more consistent (0-1 scale ideally)
    """
    if not splits or len(splits) < 2:
        return None
    
    times = [s.time_seconds for s in sorted(splits, key=lambda x: x.round_number)]
    
    # Calculate drift (first half vs second half)
    mid = len(times) // 2
    first_half = times[:mid]
    second_half = times[mid:]
    
    first_half_avg = mean(first_half) if first_half else 0
    second_half_avg = mean(second_half) if second_half else 0
    
    if first_half_avg > 0:
        drift = (second_half_avg - first_half_avg) / first_half_avg
    else:
        drift = None
    
    # Calculate spread (max - min) / avg
    avg_time = mean(times)
    if avg_time > 0:
        spread = (max(times) - min(times)) / avg_time
    else:
        spread = None
    
    # Calculate consistency (1 - coefficient of variation)
    if len(times) >= 2 and avg_time > 0:
        std = stdev(times)
        cv = std / avg_time  # Coefficient of variation
        consistency = max(0, 1 - cv)  # Clamp to non-negative
    else:
        consistency = None
    
    return RepeatabilityMetrics(
        drift=round(drift, 4) if drift is not None else None,
        spread=round(spread, 4) if spread is not None else None,
        consistency=round(consistency, 4) if consistency is not None else None,
        first_half_avg=round(first_half_avg, 2) if first_half_avg else None,
        second_half_avg=round(second_half_avg, 2) if second_half_avg else None,
        best_bout_time=min(times),
        worst_bout_time=max(times)
    )


def calculate_metrics(
    workout_ewu: WorkoutEWU,
    total_time_seconds: int,
    splits: Optional[List[SplitData]] = None
) -> ComputedMetrics:
    """
    Calculate all metrics for a workout.
    
    Args:
        workout_ewu: Computed EWU breakdown from EWU calculator
        total_time_seconds: Total workout duration in seconds
        splits: Optional list of round/bout times
        
    Returns:
        ComputedMetrics with all derived values
    """
    # Calculate density power
    density_per_min, density_per_sec = calculate_density_power(
        workout_ewu.total_ewu,
        total_time_seconds
    )
    
    # Calculate active power (if splits provided)
    active_power = None
    if splits and len(splits) > 0 and len(workout_ewu.rounds) > 0:
        round_ewu = workout_ewu.rounds[0].total_ewu
        active_power = calculate_active_power(round_ewu, splits)
    
    # Calculate repeatability (if splits provided)
    repeatability = calculate_repeatability(splits) if splits else None
    
    # Calculate total active time and rest time
    total_active = None
    rest_seconds = None
    if splits:
        total_active = sum(s.time_seconds for s in splits)
        rest_seconds = total_time_seconds - total_active
    
    return ComputedMetrics(
        total_ewu=workout_ewu.total_ewu,
        density_power_per_min=density_per_min,
        density_power_per_sec=density_per_sec,
        active_power=active_power,
        repeatability=repeatability,
        lift_ewu=workout_ewu.lift_ewu,
        machine_ewu=workout_ewu.machine_ewu,
        gymnastics_ewu=workout_ewu.gymnastics_ewu,
        lift_share=workout_ewu.lift_share,
        machine_share=workout_ewu.machine_share,
        gymnastics_share=workout_ewu.gymnastics_share,
        total_time_seconds=total_time_seconds,
        total_active_seconds=round(total_active, 2) if total_active else None,
        rest_seconds=round(rest_seconds, 2) if rest_seconds is not None else None
    )


# Example usage and verification
if __name__ == "__main__":
    from .ewu_calculator import (
        MovementData, MovementType, calculate_workout_ewu
    )
    
    # Test with the sample workout:
    # 6 sets every 3:00
    # 10 cal Echo + 8 unbroken power snatch @95 + 10 cal Echo
    # Bout times: 90, 88, 89, 89, 96, 94 sec
    # Total session time: 18:14 (1094 seconds)
    
    movements = [
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
        MovementData(MovementType.POWER_SNATCH, reps=8, load_lb=95),
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
    ]
    
    splits = [
        SplitData(round_number=1, time_seconds=90),
        SplitData(round_number=2, time_seconds=88),
        SplitData(round_number=3, time_seconds=89),
        SplitData(round_number=4, time_seconds=89),
        SplitData(round_number=5, time_seconds=96),
        SplitData(round_number=6, time_seconds=94),
    ]
    
    workout_ewu = calculate_workout_ewu(movements, round_count=6)
    total_time = 18 * 60 + 14  # 18:14 = 1094 seconds
    
    metrics = calculate_metrics(workout_ewu, total_time, splits)
    
    print("=== Metrics Calculation ===")
    print(f"\nCore Metrics:")
    print(f"  Total EWU: {metrics.total_ewu}")
    print(f"  Density Power: {metrics.density_power_per_min:.2f} EWU/min")
    print(f"  Density Power: {metrics.density_power_per_sec:.4f} EWU/sec")
    
    if metrics.active_power:
        print(f"\nActive Power:")
        print(f"  Average: {metrics.active_power.average_active_power:.2f} EWU/min")
        print(f"  Peak: {metrics.active_power.peak_power:.2f} EWU/min")
        print(f"  Per Round: {metrics.active_power.per_round_power}")
    
    if metrics.repeatability:
        print(f"\nRepeatability:")
        print(f"  Drift: {metrics.repeatability.drift:.1%}")
        print(f"  Spread: {metrics.repeatability.spread:.1%}")
        print(f"  Consistency: {metrics.repeatability.consistency:.1%}")
        print(f"  First Half Avg: {metrics.repeatability.first_half_avg}s")
        print(f"  Second Half Avg: {metrics.repeatability.second_half_avg}s")
    
    print(f"\nModality Share:")
    print(f"  Lift: {metrics.lift_share:.1%}")
    print(f"  Machine: {metrics.machine_share:.1%}")
    
    print(f"\nTiming:")
    print(f"  Total Time: {metrics.total_time_seconds}s ({metrics.total_time_seconds/60:.1f} min)")
    print(f"  Active Time: {metrics.total_active_seconds}s")
    print(f"  Rest Time: {metrics.rest_seconds}s")
