"""
EWU (Effective Work Unit) Calculator

The core physics-based measurement system for CrossFit performance.

EWU Formulas (v1):
- Bike_EWU = echo_bike_calories (1 cal = 1 EWU)
- Lift_EWU = (load_lb * reps) / 50
- Round_EWU = sum(all movement EWUs in a round)
- Total_EWU = Round_EWU * round_count (or sum of all rounds)

Extensibility (future):
- Row_EWU = row_calories * ROW_FACTOR
- Run_EWU = meters / RUN_DIVISOR  
- Gymnastics_EWU = reps * MOVEMENT_FACTOR
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict
from decimal import Decimal


class MovementType(str, Enum):
    # Machine/Monostructural
    ECHO_BIKE = "echo_bike"
    ROWER = "rower"
    SKI_ERG = "ski_erg"
    RUN = "run"
    ASSAULT_BIKE = "assault_bike"
    
    # Barbell
    POWER_SNATCH = "power_snatch"
    SQUAT_SNATCH = "squat_snatch"
    POWER_CLEAN = "power_clean"
    SQUAT_CLEAN = "squat_clean"
    CLEAN_AND_JERK = "clean_and_jerk"
    DEADLIFT = "deadlift"
    BACK_SQUAT = "back_squat"
    FRONT_SQUAT = "front_squat"
    OVERHEAD_SQUAT = "overhead_squat"
    STRICT_PRESS = "strict_press"
    PUSH_PRESS = "push_press"
    PUSH_JERK = "push_jerk"
    SPLIT_JERK = "split_jerk"
    THRUSTER = "thruster"
    HANG_POWER_SNATCH = "hang_power_snatch"
    HANG_POWER_CLEAN = "hang_power_clean"
    HANG_SQUAT_SNATCH = "hang_squat_snatch"
    HANG_SQUAT_CLEAN = "hang_squat_clean"
    SUMO_DEADLIFT = "sumo_deadlift"
    ROMANIAN_DEADLIFT = "romanian_deadlift"
    
    # Gymnastics (placeholder)
    PULL_UP = "pull_up"
    CHEST_TO_BAR = "chest_to_bar"
    MUSCLE_UP = "muscle_up"
    BAR_MUSCLE_UP = "bar_muscle_up"
    TOES_TO_BAR = "toes_to_bar"
    HANDSTAND_PUSH_UP = "handstand_push_up"
    BOX_JUMP = "box_jump"
    BOX_JUMP_OVER = "box_jump_over"
    BURPEE = "burpee"
    BURPEE_BOX_JUMP_OVER = "burpee_box_jump_over"
    DOUBLE_UNDER = "double_under"
    WALL_BALL = "wall_ball"
    KETTLEBELL_SWING = "kettlebell_swing"
    DUMBBELL_SNATCH = "dumbbell_snatch"
    DUMBBELL_CLEAN = "dumbbell_clean"


class Modality(str, Enum):
    MACHINE = "machine"
    LIFT = "lift"
    GYMNASTICS = "gymnastics"


# Movement type to modality mapping
MOVEMENT_MODALITY: Dict[MovementType, Modality] = {
    # Machine
    MovementType.ECHO_BIKE: Modality.MACHINE,
    MovementType.ROWER: Modality.MACHINE,
    MovementType.SKI_ERG: Modality.MACHINE,
    MovementType.RUN: Modality.MACHINE,
    MovementType.ASSAULT_BIKE: Modality.MACHINE,
    
    # Barbell
    MovementType.POWER_SNATCH: Modality.LIFT,
    MovementType.SQUAT_SNATCH: Modality.LIFT,
    MovementType.POWER_CLEAN: Modality.LIFT,
    MovementType.SQUAT_CLEAN: Modality.LIFT,
    MovementType.CLEAN_AND_JERK: Modality.LIFT,
    MovementType.DEADLIFT: Modality.LIFT,
    MovementType.BACK_SQUAT: Modality.LIFT,
    MovementType.FRONT_SQUAT: Modality.LIFT,
    MovementType.OVERHEAD_SQUAT: Modality.LIFT,
    MovementType.STRICT_PRESS: Modality.LIFT,
    MovementType.PUSH_PRESS: Modality.LIFT,
    MovementType.PUSH_JERK: Modality.LIFT,
    MovementType.SPLIT_JERK: Modality.LIFT,
    MovementType.THRUSTER: Modality.LIFT,
    MovementType.HANG_POWER_SNATCH: Modality.LIFT,
    MovementType.HANG_POWER_CLEAN: Modality.LIFT,
    MovementType.HANG_SQUAT_SNATCH: Modality.LIFT,
    MovementType.HANG_SQUAT_CLEAN: Modality.LIFT,
    MovementType.SUMO_DEADLIFT: Modality.LIFT,
    MovementType.ROMANIAN_DEADLIFT: Modality.LIFT,
    
    # Gymnastics
    MovementType.PULL_UP: Modality.GYMNASTICS,
    MovementType.CHEST_TO_BAR: Modality.GYMNASTICS,
    MovementType.MUSCLE_UP: Modality.GYMNASTICS,
    MovementType.BAR_MUSCLE_UP: Modality.GYMNASTICS,
    MovementType.TOES_TO_BAR: Modality.GYMNASTICS,
    MovementType.HANDSTAND_PUSH_UP: Modality.GYMNASTICS,
    MovementType.BOX_JUMP: Modality.GYMNASTICS,
    MovementType.BOX_JUMP_OVER: Modality.GYMNASTICS,
    MovementType.BURPEE: Modality.GYMNASTICS,
    MovementType.BURPEE_BOX_JUMP_OVER: Modality.GYMNASTICS,
    MovementType.DOUBLE_UNDER: Modality.GYMNASTICS,
    MovementType.WALL_BALL: Modality.GYMNASTICS,
    MovementType.KETTLEBELL_SWING: Modality.GYMNASTICS,
    MovementType.DUMBBELL_SNATCH: Modality.GYMNASTICS,
    MovementType.DUMBBELL_CLEAN: Modality.GYMNASTICS,
}


# EWU factors for different modalities (extensible)
class EWUFactors:
    """
    EWU conversion factors.
    These can be calibrated over time based on physiological research.
    """
    # Machine factors (calories to EWU)
    ECHO_BIKE_FACTOR = 1.0  # 1 cal = 1 EWU (baseline)
    ROWER_FACTOR = 1.0      # Placeholder
    SKI_ERG_FACTOR = 1.0    # Placeholder
    ASSAULT_BIKE_FACTOR = 1.0
    
    # Lift divisor (load_lb * reps / DIVISOR = EWU)
    LIFT_DIVISOR = 50.0
    
    # Run factor (meters / DIVISOR = EWU)
    RUN_DIVISOR = 100.0     # Placeholder: 100m = 1 EWU
    
    # Gymnastics factors (reps * factor = EWU)
    # These are placeholders and should be calibrated
    GYMNASTICS_FACTORS: Dict[MovementType, float] = {
        MovementType.PULL_UP: 0.5,
        MovementType.CHEST_TO_BAR: 0.6,
        MovementType.MUSCLE_UP: 1.5,
        MovementType.BAR_MUSCLE_UP: 1.2,
        MovementType.TOES_TO_BAR: 0.4,
        MovementType.HANDSTAND_PUSH_UP: 0.8,
        MovementType.BOX_JUMP: 0.3,
        MovementType.BOX_JUMP_OVER: 0.35,
        MovementType.BURPEE: 0.5,
        MovementType.BURPEE_BOX_JUMP_OVER: 0.7,
        MovementType.DOUBLE_UNDER: 0.05,
        MovementType.WALL_BALL: 0.4,
        MovementType.KETTLEBELL_SWING: 0.3,
        MovementType.DUMBBELL_SNATCH: 0.4,
        MovementType.DUMBBELL_CLEAN: 0.4,
    }


@dataclass
class MovementData:
    """Input data for a single movement entry."""
    movement_type: MovementType
    reps: int
    load_lb: Optional[float] = None  # For barbell movements
    calories: Optional[int] = None   # For machine movements


@dataclass
class MovementEWU:
    """Computed EWU for a single movement."""
    movement_type: MovementType
    modality: Modality
    ewu: float
    raw_input: MovementData


@dataclass
class RoundEWU:
    """Computed EWU for a single round."""
    round_number: int
    movements: List[MovementEWU]
    total_ewu: float
    lift_ewu: float
    machine_ewu: float
    gymnastics_ewu: float


@dataclass
class WorkoutEWU:
    """Complete EWU breakdown for a workout."""
    rounds: List[RoundEWU]
    total_ewu: float
    lift_ewu: float
    machine_ewu: float
    gymnastics_ewu: float
    lift_share: float      # lift_ewu / total_ewu
    machine_share: float   # machine_ewu / total_ewu
    gymnastics_share: float


def get_modality(movement_type: MovementType) -> Modality:
    """Get the modality for a movement type."""
    return MOVEMENT_MODALITY.get(movement_type, Modality.GYMNASTICS)


def calculate_movement_ewu(movement: MovementData) -> MovementEWU:
    """
    Calculate EWU for a single movement.
    
    Formulas:
    - Machine (bike/row): EWU = calories * factor
    - Lift (barbell): EWU = (load_lb * reps) / 50
    - Gymnastics: EWU = reps * movement_factor (placeholder)
    """
    modality = get_modality(movement.movement_type)
    ewu = 0.0
    
    if modality == Modality.MACHINE:
        # Machine movements use calories
        calories = movement.calories or 0
        
        if movement.movement_type == MovementType.ECHO_BIKE:
            ewu = calories * EWUFactors.ECHO_BIKE_FACTOR
        elif movement.movement_type == MovementType.ROWER:
            ewu = calories * EWUFactors.ROWER_FACTOR
        elif movement.movement_type == MovementType.SKI_ERG:
            ewu = calories * EWUFactors.SKI_ERG_FACTOR
        elif movement.movement_type == MovementType.ASSAULT_BIKE:
            ewu = calories * EWUFactors.ASSAULT_BIKE_FACTOR
        elif movement.movement_type == MovementType.RUN:
            # For run, we might use meters instead of calories
            # This is a placeholder
            ewu = (movement.reps or 0) / EWUFactors.RUN_DIVISOR
        else:
            ewu = calories * 1.0  # Default factor
            
    elif modality == Modality.LIFT:
        # Barbell movements use load * reps
        load = movement.load_lb or 0
        reps = movement.reps or 0
        ewu = (load * reps) / EWUFactors.LIFT_DIVISOR
        
    elif modality == Modality.GYMNASTICS:
        # Gymnastics use rep-based factors
        reps = movement.reps or 0
        factor = EWUFactors.GYMNASTICS_FACTORS.get(movement.movement_type, 0.3)
        ewu = reps * factor
    
    return MovementEWU(
        movement_type=movement.movement_type,
        modality=modality,
        ewu=round(ewu, 2),
        raw_input=movement
    )


def calculate_round_ewu(movements: List[MovementData], round_number: int = 1) -> RoundEWU:
    """
    Calculate total EWU for a single round.
    """
    movement_ewus = [calculate_movement_ewu(m) for m in movements]
    
    lift_ewu = sum(m.ewu for m in movement_ewus if m.modality == Modality.LIFT)
    machine_ewu = sum(m.ewu for m in movement_ewus if m.modality == Modality.MACHINE)
    gymnastics_ewu = sum(m.ewu for m in movement_ewus if m.modality == Modality.GYMNASTICS)
    total_ewu = lift_ewu + machine_ewu + gymnastics_ewu
    
    return RoundEWU(
        round_number=round_number,
        movements=movement_ewus,
        total_ewu=round(total_ewu, 2),
        lift_ewu=round(lift_ewu, 2),
        machine_ewu=round(machine_ewu, 2),
        gymnastics_ewu=round(gymnastics_ewu, 2)
    )


def calculate_workout_ewu(
    movements: List[MovementData],
    round_count: int = 1
) -> WorkoutEWU:
    """
    Calculate total EWU for an entire workout.
    
    For interval workouts, movements represent one round and are multiplied.
    For chippers, movements represent the entire workout (round_count = 1).
    """
    # Calculate single round EWU
    round_ewu = calculate_round_ewu(movements)
    
    # Create rounds (for intervals, same structure repeated)
    rounds = [
        RoundEWU(
            round_number=i + 1,
            movements=round_ewu.movements,
            total_ewu=round_ewu.total_ewu,
            lift_ewu=round_ewu.lift_ewu,
            machine_ewu=round_ewu.machine_ewu,
            gymnastics_ewu=round_ewu.gymnastics_ewu
        )
        for i in range(round_count)
    ]
    
    # Total EWU = round EWU * round_count
    total_ewu = round_ewu.total_ewu * round_count
    lift_ewu = round_ewu.lift_ewu * round_count
    machine_ewu = round_ewu.machine_ewu * round_count
    gymnastics_ewu = round_ewu.gymnastics_ewu * round_count
    
    # Calculate shares
    if total_ewu > 0:
        lift_share = lift_ewu / total_ewu
        machine_share = machine_ewu / total_ewu
        gymnastics_share = gymnastics_ewu / total_ewu
    else:
        lift_share = machine_share = gymnastics_share = 0.0
    
    return WorkoutEWU(
        rounds=rounds,
        total_ewu=round(total_ewu, 2),
        lift_ewu=round(lift_ewu, 2),
        machine_ewu=round(machine_ewu, 2),
        gymnastics_ewu=round(gymnastics_ewu, 2),
        lift_share=round(lift_share, 4),
        machine_share=round(machine_share, 4),
        gymnastics_share=round(gymnastics_share, 4)
    )


# Example usage and verification
if __name__ == "__main__":
    # Test with the sample workout:
    # 6 sets every 3:00
    # 10 cal Echo + 8 unbroken power snatch @95 + 10 cal Echo
    
    movements = [
        MovementData(
            movement_type=MovementType.ECHO_BIKE,
            reps=1,
            calories=10
        ),
        MovementData(
            movement_type=MovementType.POWER_SNATCH,
            reps=8,
            load_lb=95
        ),
        MovementData(
            movement_type=MovementType.ECHO_BIKE,
            reps=1,
            calories=10
        ),
    ]
    
    workout_ewu = calculate_workout_ewu(movements, round_count=6)
    
    print("=== EWU Calculation ===")
    print(f"Round EWU breakdown:")
    round_ewu = workout_ewu.rounds[0]
    for m in round_ewu.movements:
        print(f"  {m.movement_type.value}: {m.ewu} EWU")
    print(f"  Round Total: {round_ewu.total_ewu} EWU")
    print(f"\nWorkout Totals (6 rounds):")
    print(f"  Total EWU: {workout_ewu.total_ewu}")
    print(f"  Lift EWU: {workout_ewu.lift_ewu}")
    print(f"  Machine EWU: {workout_ewu.machine_ewu}")
    print(f"  Lift Share: {workout_ewu.lift_share:.1%}")
    print(f"  Machine Share: {workout_ewu.machine_share:.1%}")
