"""
Workout Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TemplateTypeEnum(str, Enum):
    INTERVAL = "interval"
    CHIPPER = "chipper"
    SPRINT_TEST = "sprint_test"
    THRESHOLD = "threshold"
    ENDURANCE = "endurance"
    STRENGTH_SESSION = "strength_session"
    MONOSTRUCTURAL_TEST = "monostructural_test"
    CUSTOM = "custom"


class MovementTypeEnum(str, Enum):
    # Machine
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
    
    # Gymnastics
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


# Movement Input/Output Schemas
class MovementInput(BaseModel):
    """Schema for movement entry input."""
    movement_type: MovementTypeEnum
    reps: int = Field(..., ge=1)
    load_lb: Optional[float] = Field(None, ge=0, le=1000)
    calories: Optional[int] = Field(None, ge=0, le=500)
    order_index: int = Field(..., ge=0)
    
    @field_validator('load_lb', 'calories')
    @classmethod
    def validate_movement_context(cls, v, info):
        return v


class MovementResponse(BaseModel):
    """Schema for movement response."""
    id: str
    movement_type: str
    modality: str
    reps: int
    load_lb: Optional[float] = None
    calories: Optional[int] = None
    order_index: int
    
    class Config:
        from_attributes = True


# Split Input/Output Schemas
class SplitInput(BaseModel):
    """Schema for split/round time input."""
    round_number: int = Field(..., ge=1)
    time_seconds: float = Field(..., gt=0, le=3600)


class SplitResponse(BaseModel):
    """Schema for split response."""
    round_number: int
    time_seconds: float
    
    class Config:
        from_attributes = True


# Metrics Schemas
class RepeatabilityResponse(BaseModel):
    """Schema for repeatability metrics."""
    drift: Optional[float] = None
    spread: Optional[float] = None
    consistency: Optional[float] = None
    first_half_avg: Optional[float] = None
    second_half_avg: Optional[float] = None
    best_bout_time: Optional[float] = None
    worst_bout_time: Optional[float] = None


class ActivePowerResponse(BaseModel):
    """Schema for active power metrics."""
    average_active_power: float
    per_round_power: List[float]
    peak_power: float
    lowest_power: float


class MetricsResponse(BaseModel):
    """Schema for computed metrics response."""
    total_ewu: float
    density_power_min: float
    density_power_sec: float
    active_power: Optional[ActivePowerResponse] = None
    repeatability: Optional[RepeatabilityResponse] = None
    lift_ewu: float
    machine_ewu: float
    gymnastics_ewu: float = 0
    lift_share: float
    machine_share: float
    gymnastics_share: float = 0
    total_time_seconds: int
    total_active_seconds: Optional[float] = None
    rest_seconds: Optional[float] = None
    computed_at: Optional[datetime] = None


# Workout Input/Output Schemas
class WorkoutCreate(BaseModel):
    """Schema for creating a workout."""
    name: Optional[str] = Field(None, max_length=255)
    template_type: TemplateTypeEnum
    total_time_seconds: int = Field(..., gt=0, le=86400)  # Max 24 hours
    round_count: int = Field(1, ge=1, le=100)
    performed_at: datetime
    notes: Optional[str] = None
    movements: List[MovementInput] = Field(..., min_length=1)
    splits: Optional[List[SplitInput]] = None


class WorkoutUpdate(BaseModel):
    """Schema for updating a workout."""
    name: Optional[str] = Field(None, max_length=255)
    total_time_seconds: Optional[int] = Field(None, gt=0, le=86400)
    round_count: Optional[int] = Field(None, ge=1, le=100)
    notes: Optional[str] = None
    movements: Optional[List[MovementInput]] = None
    splits: Optional[List[SplitInput]] = None


class WorkoutSummary(BaseModel):
    """Schema for workout list item."""
    id: str
    name: Optional[str]
    workout_type: Optional[str]
    template_type: str
    total_time_seconds: int
    performed_at: datetime
    total_ewu: Optional[float] = None
    density_power_min: Optional[float] = None
    
    class Config:
        from_attributes = True


class WorkoutResponse(BaseModel):
    """Schema for full workout response."""
    id: str
    name: Optional[str]
    workout_type: Optional[str]
    template_type: str
    total_time_seconds: int
    round_count: int
    performed_at: datetime
    notes: Optional[str]
    created_at: datetime
    movements: List[MovementResponse]
    splits: List[SplitResponse]
    metrics: Optional[MetricsResponse] = None
    
    class Config:
        from_attributes = True


class WorkoutCreateResponse(BaseModel):
    """Schema for workout creation response."""
    workout: WorkoutResponse
    metrics: MetricsResponse
    domains_updated: List[str]


class WorkoutListResponse(BaseModel):
    """Schema for paginated workout list."""
    workouts: List[WorkoutSummary]
    pagination: dict


class PercentileRank(BaseModel):
    """Schema for percentile ranking info."""
    workout_type: str
    density_power_percentile: Optional[float] = None
    sample_size: int = 0
