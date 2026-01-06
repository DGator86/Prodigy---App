#!/usr/bin/env python3
"""
Seed Data with Example Workout Calculation

This script demonstrates the complete calculation flow using the sample workout:
- 6 sets every 3:00
- 10 cal Echo + 8 unbroken power snatch @95 + 10 cal Echo
- 6 bout times: 90, 88, 89, 89, 96, 94 sec
- Total session time: 18:14 (1094 seconds)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine import (
    MovementData,
    MovementType,
    SplitData,
    calculate_workout_ewu,
    calculate_metrics,
    classify_workout,
    TemplateType,
)


def calculate_sample_workout():
    """
    Calculate metrics for the sample workout.
    
    Workout:
    - 6 sets every 3:00
    - Each set: 10 cal Echo + 8 power snatch @95lb + 10 cal Echo
    - Bout times: 90, 88, 89, 89, 96, 94 seconds
    - Total time: 18:14 (1094 seconds)
    """
    print("=" * 60)
    print("CROSSFIT PERFORMANCE ENGINE - SAMPLE WORKOUT CALCULATION")
    print("=" * 60)
    
    # Define movements for one round
    movements = [
        MovementData(
            movement_type=MovementType.ECHO_BIKE,
            reps=1,
            calories=10  # 10 cal echo bike
        ),
        MovementData(
            movement_type=MovementType.POWER_SNATCH,
            reps=8,
            load_lb=95  # 8 power snatch @ 95 lb
        ),
        MovementData(
            movement_type=MovementType.ECHO_BIKE,
            reps=1,
            calories=10  # 10 cal echo bike
        ),
    ]
    
    # Define split times
    splits = [
        SplitData(round_number=1, time_seconds=90),
        SplitData(round_number=2, time_seconds=88),
        SplitData(round_number=3, time_seconds=89),
        SplitData(round_number=4, time_seconds=89),
        SplitData(round_number=5, time_seconds=96),
        SplitData(round_number=6, time_seconds=94),
    ]
    
    total_time_seconds = 18 * 60 + 14  # 18:14 = 1094 seconds
    round_count = 6
    
    print("\n" + "-" * 60)
    print("WORKOUT DEFINITION")
    print("-" * 60)
    print(f"Template: E3MOM (Every 3 Minutes On the Minute)")
    print(f"Rounds: {round_count}")
    print(f"Total Time: {total_time_seconds}s ({total_time_seconds/60:.2f} min)")
    print("\nMovements per round:")
    for m in movements:
        if m.calories:
            print(f"  - {m.movement_type.value}: {m.calories} cal")
        else:
            print(f"  - {m.movement_type.value}: {m.reps} reps @ {m.load_lb} lb")
    print("\nSplit times:")
    for s in splits:
        print(f"  Round {s.round_number}: {s.time_seconds}s")
    
    # Step 1: Calculate EWU
    print("\n" + "-" * 60)
    print("STEP 1: EWU CALCULATION")
    print("-" * 60)
    
    workout_ewu = calculate_workout_ewu(movements, round_count=round_count)
    
    # Show per-movement breakdown
    round_ewu = workout_ewu.rounds[0]
    print("\nPer-movement EWU (one round):")
    for m in round_ewu.movements:
        if m.modality.value == "machine":
            print(f"  {m.movement_type.value}:")
            print(f"    Formula: calories × 1.0 = {m.raw_input.calories} × 1.0")
            print(f"    EWU: {m.ewu}")
        else:
            print(f"  {m.movement_type.value}:")
            print(f"    Formula: (load × reps) / 50 = ({m.raw_input.load_lb} × {m.raw_input.reps}) / 50")
            print(f"    EWU: {m.ewu}")
    
    print(f"\nRound EWU: {round_ewu.total_ewu}")
    print(f"  - Bike EWU: {round_ewu.machine_ewu}")
    print(f"  - Lift EWU: {round_ewu.lift_ewu}")
    
    print(f"\nTotal EWU ({round_count} rounds):")
    print(f"  {round_ewu.total_ewu} × {round_count} = {workout_ewu.total_ewu}")
    
    # Step 2: Calculate Metrics
    print("\n" + "-" * 60)
    print("STEP 2: METRICS CALCULATION")
    print("-" * 60)
    
    metrics = calculate_metrics(workout_ewu, total_time_seconds, splits)
    
    print("\n>>> DENSITY POWER <<<")
    print(f"Formula: Total_EWU / Total_Time")
    print(f"  Per minute: {workout_ewu.total_ewu} / {total_time_seconds/60:.2f} min = {metrics.density_power_per_min:.2f} EWU/min")
    print(f"  Per second: {workout_ewu.total_ewu} / {total_time_seconds} s = {metrics.density_power_per_sec:.4f} EWU/s")
    
    print("\n>>> ACTIVE POWER <<<")
    if metrics.active_power:
        print(f"Formula: Round_EWU / Bout_Time (per round)")
        print(f"Round EWU: {round_ewu.total_ewu}")
        print("\nPer-round calculation:")
        for i, (split, power) in enumerate(zip(splits, metrics.active_power.per_round_power)):
            bout_min = split.time_seconds / 60
            print(f"  Round {i+1}: {round_ewu.total_ewu} / {bout_min:.2f} min = {power:.2f} EWU/min")
        print(f"\nAverage Active Power: {metrics.active_power.average_active_power:.2f} EWU/min")
        print(f"Peak Power: {metrics.active_power.peak_power:.2f} EWU/min")
        print(f"Lowest Power: {metrics.active_power.lowest_power:.2f} EWU/min")
    
    print("\n>>> REPEATABILITY <<<")
    if metrics.repeatability:
        print("Split times:", [s.time_seconds for s in splits])
        print(f"\nDrift (fatigue indicator):")
        print(f"  First half average: {metrics.repeatability.first_half_avg}s")
        print(f"  Second half average: {metrics.repeatability.second_half_avg}s")
        print(f"  Formula: (second_half - first_half) / first_half")
        print(f"  Drift: {metrics.repeatability.drift:.4f} ({metrics.repeatability.drift*100:.1f}%)")
        print(f"  Interpretation: {'Slowing down' if metrics.repeatability.drift > 0 else 'Getting faster'}")
        
        print(f"\nSpread (consistency):")
        print(f"  Best bout: {metrics.repeatability.best_bout_time}s")
        print(f"  Worst bout: {metrics.repeatability.worst_bout_time}s")
        avg_time = sum(s.time_seconds for s in splits) / len(splits)
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Formula: (max - min) / avg")
        print(f"  Spread: {metrics.repeatability.spread:.4f} ({metrics.repeatability.spread*100:.1f}%)")
        
        print(f"\nConsistency (1 - CV):")
        print(f"  Consistency: {metrics.repeatability.consistency:.4f} ({metrics.repeatability.consistency*100:.1f}%)")
    
    print("\n>>> MODALITY SHARE <<<")
    print(f"Lift EWU: {workout_ewu.lift_ewu} ({workout_ewu.lift_share*100:.1f}%)")
    print(f"Machine EWU: {workout_ewu.machine_ewu} ({workout_ewu.machine_share*100:.1f}%)")
    
    # Step 3: Classify Workout Type
    print("\n" + "-" * 60)
    print("STEP 3: WORKOUT TYPE CLASSIFICATION")
    print("-" * 60)
    
    type_result = classify_workout(
        movements=movements,
        workout_ewu=workout_ewu,
        total_time_seconds=total_time_seconds,
        round_count=round_count,
        has_splits=True,
        template_type=TemplateType.INTERVAL
    )
    
    print(f"\nClassified Type: {type_result.workout_type.value.upper()}")
    print(f"Confidence: {type_result.confidence*100:.0f}%")
    print(f"Reasoning: {type_result.reasoning}")
    print(f"\nCharacteristics detected:")
    print(f"  - Is Interval: {type_result.is_interval}")
    print(f"  - Duration Category: {type_result.duration_category}")
    print(f"  - Is Monostructural: {type_result.is_monostructural}")
    print(f"  - Is Strength Focused: {type_result.is_strength_focused}")
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPUTED OUTPUT SUMMARY")
    print("=" * 60)
    print(f"""
┌─────────────────────────────────────────────────────────┐
│ TOTAL EWU:           {workout_ewu.total_ewu:>8.2f}                        │
│ DENSITY POWER:       {metrics.density_power_per_min:>8.2f} EWU/min              │
│ ACTIVE POWER:        {metrics.active_power.average_active_power if metrics.active_power else 'N/A':>8.2f} EWU/min              │
│ REPEATABILITY:                                          │
│   - Drift:           {metrics.repeatability.drift*100 if metrics.repeatability else 0:>8.1f}%                       │
│   - Spread:          {metrics.repeatability.spread*100 if metrics.repeatability else 0:>8.1f}%                       │
│   - Consistency:     {metrics.repeatability.consistency*100 if metrics.repeatability else 0:>8.1f}%                       │
│ MODALITY SHARE:                                         │
│   - Lift:            {workout_ewu.lift_share*100:>8.1f}%                       │
│   - Machine:         {workout_ewu.machine_share*100:>8.1f}%                       │
│ WORKOUT TYPE:        {type_result.workout_type.value.upper():>8s}                        │
└─────────────────────────────────────────────────────────┘
""")
    
    print("\n>>> DOMAINS UPDATED BY THIS WORKOUT <<<")
    print("  ✓ Mixed-Modal Capacity (density power logged)")
    print("  ✓ Strength Output (lift EWU logged)")
    print("  ✓ Repeatability (split times provided)")
    print("  ✗ Monostructural Output (not 100% machine)")
    print("  ✗ Sprint/Power Capacity (not a sprint test)")
    
    return {
        "total_ewu": workout_ewu.total_ewu,
        "density_power_min": metrics.density_power_per_min,
        "density_power_sec": metrics.density_power_per_sec,
        "active_power": metrics.active_power.average_active_power if metrics.active_power else None,
        "repeatability_drift": metrics.repeatability.drift if metrics.repeatability else None,
        "repeatability_spread": metrics.repeatability.spread if metrics.repeatability else None,
        "repeatability_consistency": metrics.repeatability.consistency if metrics.repeatability else None,
        "lift_share": workout_ewu.lift_share,
        "machine_share": workout_ewu.machine_share,
        "workout_type": type_result.workout_type.value
    }


if __name__ == "__main__":
    results = calculate_sample_workout()
    
    print("\n" + "=" * 60)
    print("JSON OUTPUT (for API response)")
    print("=" * 60)
    import json
    print(json.dumps(results, indent=2))
