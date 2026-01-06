"""
Domain scores and trends API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ...db.database import get_db
from ...services.auth_service import AuthService
from ...services.workout_service import WorkoutService
from ...core.security import oauth2_scheme
from ...schemas.domain import (
    DomainScoreResponse,
    DomainsResponse,
    RadarChartResponse,
    RadarDataPoint,
    DomainDetailResponse,
    TrendsResponse,
    TrendMetric,
    TrendDataPoint,
)

router = APIRouter(prefix="/domains", tags=["Domains & Radar"])


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> str:
    """Dependency to get current user ID."""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user.id


# Domain labels for display
DOMAIN_LABELS = {
    "strength_output": "Strength",
    "monostructural_output": "Monostructural",
    "mixed_modal_capacity": "Mixed-Modal",
    "sprint_power_capacity": "Sprint/Power",
    "repeatability": "Repeatability",
}


@router.get("", response_model=DomainsResponse)
def get_domain_scores(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all domain scores for radar chart.
    
    Returns scores for all 5 domains:
    - Strength Output
    - Monostructural Output
    - Mixed-Modal Capacity
    - Sprint/Power Capacity
    - Repeatability
    
    Each domain includes:
    - raw_value: The actual metric value
    - normalized_score: 0-100 percentile score
    - sample_count: Number of workouts contributing
    - confidence: no_data, low, medium, or high
    """
    workout_service = WorkoutService(db)
    
    scores = workout_service.get_domain_scores(user_id)
    
    domain_responses = []
    last_updated = None
    
    for score in scores:
        domain_responses.append(DomainScoreResponse(
            domain=score.domain,
            raw_value=score.raw_value,
            normalized_score=score.normalized_score,
            sample_count=score.sample_count,
            confidence=score.confidence
        ))
        
        if score.updated_at and (last_updated is None or score.updated_at > last_updated):
            last_updated = score.updated_at
    
    return DomainsResponse(
        domains=domain_responses,
        last_updated=last_updated
    )


@router.get("/radar", response_model=RadarChartResponse)
def get_radar_chart(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get radar chart visualization data.
    
    Returns data formatted for radar/spider chart rendering,
    including labels and has_data flags for UI handling.
    """
    workout_service = WorkoutService(db)
    
    scores = workout_service.get_domain_scores(user_id)
    
    data = []
    last_updated = None
    
    for score in scores:
        data.append(RadarDataPoint(
            domain=score.domain,
            label=DOMAIN_LABELS.get(score.domain, score.domain),
            score=score.normalized_score,
            confidence=score.confidence,
            has_data=score.sample_count > 0
        ))
        
        if score.updated_at and (last_updated is None or score.updated_at > last_updated):
            last_updated = score.updated_at
    
    return RadarChartResponse(
        data=data,
        last_updated=last_updated
    )


@router.get("/{domain}", response_model=DomainDetailResponse)
def get_domain_detail(
    domain: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed breakdown for a specific domain.
    
    Returns:
    - Current score and confidence
    - Contributing workouts
    - Historical score progression
    """
    valid_domains = [
        "strength_output",
        "monostructural_output",
        "mixed_modal_capacity",
        "sprint_power_capacity",
        "repeatability"
    ]
    
    if domain not in valid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domain. Must be one of: {valid_domains}"
        )
    
    workout_service = WorkoutService(db)
    
    scores = workout_service.get_domain_scores(user_id)
    
    domain_score = next((s for s in scores if s.domain == domain), None)
    
    if not domain_score:
        return DomainDetailResponse(
            domain=domain,
            raw_value=None,
            normalized_score=None,
            sample_count=0,
            confidence="no_data",
            has_data=False,
            updated_at=None,
            contributing_workouts=[]
        )
    
    return DomainDetailResponse(
        domain=domain,
        raw_value=domain_score.raw_value,
        normalized_score=domain_score.normalized_score,
        sample_count=domain_score.sample_count,
        confidence=domain_score.confidence,
        has_data=domain_score.sample_count > 0,
        updated_at=domain_score.updated_at,
        contributing_workouts=[]  # Could be populated with distribution data
    )


# Trends endpoint
trends_router = APIRouter(prefix="/trends", tags=["Trends"])


@trends_router.get("", response_model=TrendsResponse)
def get_trends(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get trend data for dashboard charts.
    
    **Query parameters:**
    - period: Time period (7d, 30d, or 90d)
    
    Returns trend data for:
    - Density Power
    - Repeatability
    - Total EWU
    """
    workout_service = WorkoutService(db)
    
    trends = workout_service.get_trends(user_id, period)
    
    # Build response
    density_power = None
    if trends["density_power"]["data"]:
        data = [
            TrendDataPoint(
                date=datetime.fromisoformat(d["date"]),
                value=d["value"]
            )
            for d in trends["density_power"]["data"]
        ]
        density_power = TrendMetric(
            data=data,
            average=trends["density_power"]["average"]
        )
    
    repeatability = None
    if trends["repeatability"]["data"]:
        data = [
            TrendDataPoint(
                date=datetime.fromisoformat(d["date"]),
                value=d["value"]
            )
            for d in trends["repeatability"]["data"]
        ]
        repeatability = TrendMetric(
            data=data,
            average=trends["repeatability"]["average"]
        )
    
    total_ewu = None
    if trends["total_ewu"]["data"]:
        data = [
            TrendDataPoint(
                date=datetime.fromisoformat(d["date"]),
                value=d["value"]
            )
            for d in trends["total_ewu"]["data"]
        ]
        total_ewu = TrendMetric(
            data=data,
            average=trends["total_ewu"]["sum"] / len(data) if data else None
        )
    
    return TrendsResponse(
        period=period,
        density_power=density_power,
        repeatability=repeatability,
        total_ewu=total_ewu
    )


# Include trends router
router.include_router(trends_router)
