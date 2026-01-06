"""
Workout Typer

Auto-classifies workouts based on structure and content.

Workout Types:
- Sprint: total_time < 5 min (300s)
- Threshold: 5 min <= total_time < 15 min (300-900s)
- Endurance: total_time >= 15 min (900s+)
- Interval: round_count > 1 AND has splits
- Chipper: many movements (>4) AND single pass (round_count == 1)
- Strength: lift_share > 80% AND low reps per set
- Monostructural: machine_share == 100%

Priority order for classification:
1. Monostructural (100% machine)
2. Strength (>80% lift, heavy/low rep)
3. Interval (has splits, multiple rounds)
4. Chipper (many movements, single pass)
5. Time-based (sprint/threshold/endurance)
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from .ewu_calculator import MovementData, WorkoutEWU, Modality, get_modality


class WorkoutType(str, Enum):
    SPRINT = "sprint"
    THRESHOLD = "threshold"
    ENDURANCE = "endurance"
    INTERVAL = "interval"
    CHIPPER = "chipper"
    STRENGTH = "strength"
    MONOSTRUCTURAL = "monostructural"


class TemplateType(str, Enum):
    INTERVAL = "interval"
    CHIPPER = "chipper"
    SPRINT_TEST = "sprint_test"
    THRESHOLD = "threshold"
    ENDURANCE = "endurance"
    STRENGTH_SESSION = "strength_session"
    MONOSTRUCTURAL_TEST = "monostructural_test"
    CUSTOM = "custom"


@dataclass
class WorkoutTypeResult:
    """Result of workout type classification."""
    workout_type: WorkoutType
    confidence: float  # 0-1 confidence in classification
    reasoning: str
    
    # Characteristics detected
    is_interval: bool
    is_chipper: bool
    is_monostructural: bool
    is_strength_focused: bool
    duration_category: str  # "sprint", "threshold", "endurance"


# Time thresholds (in seconds)
SPRINT_THRESHOLD = 300      # 5 minutes
THRESHOLD_THRESHOLD = 900   # 15 minutes

# Composition thresholds
MONOSTRUCTURAL_THRESHOLD = 1.0   # 100% machine
STRENGTH_LIFT_THRESHOLD = 0.80   # 80% lift share
CHIPPER_MIN_MOVEMENTS = 4        # At least 4 distinct movements

# Strength detection
STRENGTH_MAX_REPS_PER_SET = 5    # Heavy lifts usually 1-5 reps


def get_duration_category(total_time_seconds: int) -> str:
    """Classify workout by duration."""
    if total_time_seconds < SPRINT_THRESHOLD:
        return "sprint"
    elif total_time_seconds < THRESHOLD_THRESHOLD:
        return "threshold"
    else:
        return "endurance"


def is_strength_workout(
    movements: List[MovementData],
    workout_ewu: WorkoutEWU
) -> bool:
    """
    Determine if workout is strength-focused.
    
    Criteria:
    - Lift share > 80%
    - Average reps per lift movement <= 5
    """
    if workout_ewu.lift_share < STRENGTH_LIFT_THRESHOLD:
        return False
    
    # Check rep ranges for lift movements
    lift_movements = [
        m for m in movements 
        if get_modality(m.movement_type) == Modality.LIFT
    ]
    
    if not lift_movements:
        return False
    
    avg_reps = sum(m.reps for m in lift_movements) / len(lift_movements)
    
    return avg_reps <= STRENGTH_MAX_REPS_PER_SET


def classify_workout(
    movements: List[MovementData],
    workout_ewu: WorkoutEWU,
    total_time_seconds: int,
    round_count: int = 1,
    has_splits: bool = False,
    template_type: Optional[TemplateType] = None
) -> WorkoutTypeResult:
    """
    Classify a workout based on its characteristics.
    
    Classification priority:
    1. Monostructural (100% machine) - highest specificity
    2. Strength (>80% lift, low reps)
    3. Interval (multiple rounds with splits)
    4. Chipper (many movements, single pass)
    5. Time-based fallback (sprint/threshold/endurance)
    """
    # Detect characteristics
    is_mono = workout_ewu.machine_share >= MONOSTRUCTURAL_THRESHOLD
    is_strength = is_strength_workout(movements, workout_ewu)
    is_interval = round_count > 1 and has_splits
    unique_movements = len(set(m.movement_type for m in movements))
    is_chipper = unique_movements >= CHIPPER_MIN_MOVEMENTS and round_count == 1
    duration_cat = get_duration_category(total_time_seconds)
    
    # Classification logic with confidence
    workout_type: WorkoutType
    confidence: float
    reasoning: str
    
    # 1. Monostructural (highest priority when 100% machine)
    if is_mono:
        workout_type = WorkoutType.MONOSTRUCTURAL
        confidence = 1.0
        reasoning = "100% machine work (bike/row/ski/run only)"
    
    # 2. Strength session
    elif is_strength:
        workout_type = WorkoutType.STRENGTH
        confidence = 0.9
        reasoning = f">{STRENGTH_LIFT_THRESHOLD:.0%} lift share with low rep sets"
    
    # 3. Interval (with splits)
    elif is_interval:
        workout_type = WorkoutType.INTERVAL
        confidence = 0.95
        reasoning = f"{round_count} rounds with tracked split times"
    
    # 4. Chipper (many movements, single pass)
    elif is_chipper:
        workout_type = WorkoutType.CHIPPER
        confidence = 0.85
        reasoning = f"{unique_movements} distinct movements in single pass"
    
    # 5. Time-based fallback
    else:
        if duration_cat == "sprint":
            workout_type = WorkoutType.SPRINT
            confidence = 0.7
            reasoning = f"Short duration ({total_time_seconds}s < 5 min)"
        elif duration_cat == "threshold":
            workout_type = WorkoutType.THRESHOLD
            confidence = 0.7
            reasoning = f"Medium duration (5-15 min range)"
        else:
            workout_type = WorkoutType.ENDURANCE
            confidence = 0.7
            reasoning = f"Long duration ({total_time_seconds}s >= 15 min)"
    
    # Adjust confidence based on template hint
    if template_type:
        template_to_type = {
            TemplateType.INTERVAL: WorkoutType.INTERVAL,
            TemplateType.CHIPPER: WorkoutType.CHIPPER,
            TemplateType.SPRINT_TEST: WorkoutType.SPRINT,
            TemplateType.THRESHOLD: WorkoutType.THRESHOLD,
            TemplateType.ENDURANCE: WorkoutType.ENDURANCE,
            TemplateType.STRENGTH_SESSION: WorkoutType.STRENGTH,
            TemplateType.MONOSTRUCTURAL_TEST: WorkoutType.MONOSTRUCTURAL,
        }
        
        expected_type = template_to_type.get(template_type)
        if expected_type and expected_type == workout_type:
            confidence = min(1.0, confidence + 0.1)
        elif expected_type and expected_type != workout_type:
            # Template suggests different type - slight confidence reduction
            confidence = max(0.5, confidence - 0.1)
            reasoning += f" (template suggested {template_type.value})"
    
    return WorkoutTypeResult(
        workout_type=workout_type,
        confidence=round(confidence, 2),
        reasoning=reasoning,
        is_interval=is_interval,
        is_chipper=is_chipper,
        is_monostructural=is_mono,
        is_strength_focused=is_strength,
        duration_category=duration_cat
    )


def get_domains_for_workout_type(
    workout_type: WorkoutType,
    workout_ewu: WorkoutEWU,
    has_splits: bool = False
) -> List[str]:
    """
    Determine which domains this workout type contributes to.
    
    Domains:
    1. strength_output - Updated by lift-heavy workouts
    2. monostructural_output - Updated by mono workouts
    3. mixed_modal_capacity - Updated by mixed workouts (density power)
    4. sprint_power_capacity - Only from sprint tests (<5 min)
    5. repeatability - Updated when splits are available
    
    IMPORTANT: Only return domains where we have evidence.
    """
    domains = []
    
    # Strength output - from strength sessions or high lift share
    if workout_type == WorkoutType.STRENGTH or workout_ewu.lift_share > 0.5:
        domains.append("strength_output")
    
    # Monostructural output - from mono workouts
    if workout_type == WorkoutType.MONOSTRUCTURAL:
        domains.append("monostructural_output")
    
    # Mixed-modal capacity - from any workout with density power
    # (most workouts qualify)
    if workout_ewu.total_ewu > 0:
        domains.append("mixed_modal_capacity")
    
    # Sprint/Power capacity - ONLY from sprint workouts
    if workout_type == WorkoutType.SPRINT:
        domains.append("sprint_power_capacity")
    
    # Repeatability - only when we have split data
    if has_splits:
        domains.append("repeatability")
    
    return domains


# Example usage
if __name__ == "__main__":
    from .ewu_calculator import MovementType, calculate_workout_ewu
    
    # Test with sample workout
    movements = [
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
        MovementData(MovementType.POWER_SNATCH, reps=8, load_lb=95),
        MovementData(MovementType.ECHO_BIKE, reps=1, calories=10),
    ]
    
    workout_ewu = calculate_workout_ewu(movements, round_count=6)
    total_time = 18 * 60 + 14  # 1094 seconds
    
    result = classify_workout(
        movements=movements,
        workout_ewu=workout_ewu,
        total_time_seconds=total_time,
        round_count=6,
        has_splits=True,
        template_type=TemplateType.INTERVAL
    )
    
    print("=== Workout Type Classification ===")
    print(f"Type: {result.workout_type.value}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Reasoning: {result.reasoning}")
    print(f"\nCharacteristics:")
    print(f"  Is Interval: {result.is_interval}")
    print(f"  Is Chipper: {result.is_chipper}")
    print(f"  Is Monostructural: {result.is_monostructural}")
    print(f"  Is Strength Focused: {result.is_strength_focused}")
    print(f"  Duration Category: {result.duration_category}")
    
    domains = get_domains_for_workout_type(
        result.workout_type,
        workout_ewu,
        has_splits=True
    )
    print(f"\nDomains Updated: {domains}")
