"""
CrossFit Performance Scoring Engine

This module provides the core computation engine for:
- EWU (Effective Work Unit) calculation
- Performance metrics computation
- Workout type classification
- Score normalization
- Domain scoring for Athlete Completeness radar
"""

from .ewu_calculator import (
    MovementType,
    Modality,
    MovementData,
    MovementEWU,
    RoundEWU,
    WorkoutEWU,
    calculate_movement_ewu,
    calculate_round_ewu,
    calculate_workout_ewu,
    get_modality,
    MOVEMENT_MODALITY,
    EWUFactors,
)

from .metrics_calculator import (
    SplitData,
    RepeatabilityMetrics,
    ActivePowerMetrics,
    ComputedMetrics,
    calculate_density_power,
    calculate_active_power,
    calculate_repeatability,
    calculate_metrics,
)

from .workout_typer import (
    WorkoutType,
    TemplateType,
    WorkoutTypeResult,
    classify_workout,
    get_domains_for_workout_type,
)

from .normalizer import (
    ConfidenceLevel,
    Distribution,
    DistributionValue,
    NormalizedScore,
    DistributionStore,
    get_confidence_level,
    calculate_percentile,
    normalize_value,
    normalize_metrics,
    add_to_distribution,
    prune_distribution,
    METRIC_POLARITY,
)

from .domain_scorer import (
    DomainType,
    DomainScore,
    AthleteCompleteness,
    DomainScoreManager,
    get_qualifying_domains,
    extract_domain_metric,
    DOMAIN_PRIMARY_METRIC,
    DOMAIN_POLARITY,
)

__all__ = [
    # EWU Calculator
    "MovementType",
    "Modality",
    "MovementData",
    "MovementEWU",
    "RoundEWU",
    "WorkoutEWU",
    "calculate_movement_ewu",
    "calculate_round_ewu",
    "calculate_workout_ewu",
    "get_modality",
    "MOVEMENT_MODALITY",
    "EWUFactors",
    
    # Metrics Calculator
    "SplitData",
    "RepeatabilityMetrics",
    "ActivePowerMetrics",
    "ComputedMetrics",
    "calculate_density_power",
    "calculate_active_power",
    "calculate_repeatability",
    "calculate_metrics",
    
    # Workout Typer
    "WorkoutType",
    "TemplateType",
    "WorkoutTypeResult",
    "classify_workout",
    "get_domains_for_workout_type",
    
    # Normalizer
    "ConfidenceLevel",
    "Distribution",
    "DistributionValue",
    "NormalizedScore",
    "DistributionStore",
    "get_confidence_level",
    "calculate_percentile",
    "normalize_value",
    "normalize_metrics",
    "add_to_distribution",
    "prune_distribution",
    "METRIC_POLARITY",
    
    # Domain Scorer
    "DomainType",
    "DomainScore",
    "AthleteCompleteness",
    "DomainScoreManager",
    "get_qualifying_domains",
    "extract_domain_metric",
    "DOMAIN_PRIMARY_METRIC",
    "DOMAIN_POLARITY",
]
