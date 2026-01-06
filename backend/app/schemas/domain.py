"""
Domain and Trends Pydantic schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DomainTypeEnum(str, Enum):
    STRENGTH_OUTPUT = "strength_output"
    MONOSTRUCTURAL_OUTPUT = "monostructural_output"
    MIXED_MODAL_CAPACITY = "mixed_modal_capacity"
    SPRINT_POWER_CAPACITY = "sprint_power_capacity"
    REPEATABILITY = "repeatability"


class ConfidenceEnum(str, Enum):
    NO_DATA = "no_data"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DomainScoreResponse(BaseModel):
    """Schema for a single domain score."""
    domain: str
    raw_value: Optional[float] = None
    normalized_score: Optional[float] = None
    sample_count: int = 0
    confidence: str = "no_data"


class DomainsResponse(BaseModel):
    """Schema for all domain scores (radar chart data)."""
    domains: List[DomainScoreResponse]
    last_updated: Optional[datetime] = None


class RadarDataPoint(BaseModel):
    """Schema for a single radar chart data point."""
    domain: str
    label: str
    score: Optional[float] = None
    confidence: str
    has_data: bool


class RadarChartResponse(BaseModel):
    """Schema for radar chart visualization."""
    data: List[RadarDataPoint]
    last_updated: Optional[datetime] = None


class ContributingWorkout(BaseModel):
    """Schema for workout that contributed to a domain."""
    id: str
    name: Optional[str]
    performed_at: datetime
    metric_value: float


class DomainDetailResponse(BaseModel):
    """Schema for detailed domain breakdown."""
    domain: str
    raw_value: Optional[float]
    normalized_score: Optional[float]
    sample_count: int
    confidence: str
    has_data: bool
    updated_at: Optional[datetime]
    contributing_workouts: List[ContributingWorkout] = []


class TrendDataPoint(BaseModel):
    """Schema for a single trend data point."""
    date: datetime
    value: float


class TrendMetric(BaseModel):
    """Schema for trend data for a single metric."""
    data: List[TrendDataPoint]
    average: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    change_percent: Optional[float] = None


class TrendsResponse(BaseModel):
    """Schema for trends data."""
    period: str
    density_power: Optional[TrendMetric] = None
    repeatability: Optional[TrendMetric] = None
    total_ewu: Optional[TrendMetric] = None


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


class ExportResponse(BaseModel):
    """Schema for export metadata."""
    export_date: datetime
    format: str
    workout_count: int
    date_range: Optional[dict] = None
