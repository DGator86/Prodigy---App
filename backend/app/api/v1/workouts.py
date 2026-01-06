"""
Workout API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ...db.database import get_db
from ...services.auth_service import AuthService
from ...services.workout_service import WorkoutService
from ...core.security import oauth2_scheme
from ...schemas.workout import (
    WorkoutCreate,
    WorkoutResponse,
    WorkoutCreateResponse,
    WorkoutListResponse,
    WorkoutSummary,
    MovementResponse,
    SplitResponse,
    MetricsResponse,
    RepeatabilityResponse,
    ActivePowerResponse,
)

router = APIRouter(prefix="/workouts", tags=["Workouts"])


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


@router.post("", response_model=WorkoutCreateResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout_data: WorkoutCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Log a new workout.
    
    This endpoint:
    1. Validates workout data
    2. Computes EWU and all metrics
    3. Auto-classifies workout type
    4. Updates domain scores
    5. Returns computed metrics
    
    **Required fields:**
    - template_type: Workout template (interval, chipper, etc.)
    - total_time_seconds: Total workout duration
    - performed_at: When the workout was performed
    - movements: List of movements performed
    
    **Optional fields:**
    - name: Custom workout name
    - round_count: Number of rounds (default: 1)
    - splits: Per-round times (enables repeatability metrics)
    - notes: Free-form notes
    """
    workout_service = WorkoutService(db)
    
    try:
        workout, metrics, updated_domains = workout_service.create_workout(
            user_id=user_id,
            workout_data=workout_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Build response
    movements = [
        MovementResponse(
            id=m.id,
            movement_type=m.movement_type,
            modality=m.modality,
            reps=m.reps,
            load_lb=m.load_lb,
            calories=m.calories,
            order_index=m.order_index
        )
        for m in sorted(workout.movements, key=lambda x: x.order_index)
    ]
    
    splits = [
        SplitResponse(
            round_number=s.round_number,
            time_seconds=s.time_seconds
        )
        for s in sorted(workout.splits, key=lambda x: x.round_number)
    ]
    
    return WorkoutCreateResponse(
        workout=WorkoutResponse(
            id=workout.id,
            name=workout.name,
            workout_type=workout.workout_type,
            template_type=workout.template_type,
            total_time_seconds=workout.total_time_seconds,
            round_count=workout.round_count,
            performed_at=workout.performed_at,
            notes=workout.notes,
            created_at=workout.created_at,
            movements=movements,
            splits=splits,
            metrics=metrics
        ),
        metrics=metrics,
        domains_updated=updated_domains
    )


@router.get("", response_model=WorkoutListResponse)
def list_workouts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    workout_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List workouts with pagination and filters.
    
    **Query parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - workout_type: Filter by type (sprint, threshold, interval, etc.)
    - start_date: Filter from date
    - end_date: Filter to date
    """
    workout_service = WorkoutService(db)
    
    workouts, total = workout_service.get_workouts(
        user_id=user_id,
        page=page,
        limit=limit,
        workout_type=workout_type,
        start_date=start_date,
        end_date=end_date
    )
    
    summaries = []
    for w in workouts:
        summary = WorkoutSummary(
            id=w.id,
            name=w.name,
            workout_type=w.workout_type,
            template_type=w.template_type,
            total_time_seconds=w.total_time_seconds,
            performed_at=w.performed_at,
            total_ewu=w.metrics.total_ewu if w.metrics else None,
            density_power_min=w.metrics.density_power_min if w.metrics else None
        )
        summaries.append(summary)
    
    return WorkoutListResponse(
        workouts=summaries,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed workout information.
    
    Returns full workout data including:
    - All movements
    - All splits (if provided)
    - Computed metrics
    """
    workout_service = WorkoutService(db)
    
    workout = workout_service.get_workout(user_id, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    movements = [
        MovementResponse(
            id=m.id,
            movement_type=m.movement_type,
            modality=m.modality,
            reps=m.reps,
            load_lb=m.load_lb,
            calories=m.calories,
            order_index=m.order_index
        )
        for m in sorted(workout.movements, key=lambda x: x.order_index)
    ]
    
    splits = [
        SplitResponse(
            round_number=s.round_number,
            time_seconds=s.time_seconds
        )
        for s in sorted(workout.splits, key=lambda x: x.round_number)
    ]
    
    metrics = None
    if workout.metrics:
        m = workout.metrics
        
        repeatability = None
        if m.repeatability_drift is not None:
            repeatability = RepeatabilityResponse(
                drift=m.repeatability_drift,
                spread=m.repeatability_spread,
                consistency=m.repeatability_consistency
            )
        
        active_power = None
        if m.active_power is not None:
            active_power = ActivePowerResponse(
                average_active_power=m.active_power,
                per_round_power=m.per_round_power or [],
                peak_power=max(m.per_round_power) if m.per_round_power else m.active_power,
                lowest_power=min(m.per_round_power) if m.per_round_power else m.active_power
            )
        
        metrics = MetricsResponse(
            total_ewu=m.total_ewu,
            density_power_min=m.density_power_min,
            density_power_sec=m.density_power_sec,
            active_power=active_power,
            repeatability=repeatability,
            lift_ewu=m.lift_ewu,
            machine_ewu=m.machine_ewu,
            gymnastics_ewu=m.gymnastics_ewu,
            lift_share=m.lift_share,
            machine_share=m.machine_share,
            gymnastics_share=m.gymnastics_share,
            total_time_seconds=workout.total_time_seconds,
            total_active_seconds=m.total_active_seconds,
            rest_seconds=m.rest_seconds,
            computed_at=m.computed_at
        )
    
    return WorkoutResponse(
        id=workout.id,
        name=workout.name,
        workout_type=workout.workout_type,
        template_type=workout.template_type,
        total_time_seconds=workout.total_time_seconds,
        round_count=workout.round_count,
        performed_at=workout.performed_at,
        notes=workout.notes,
        created_at=workout.created_at,
        movements=movements,
        splits=splits,
        metrics=metrics
    )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a workout.
    
    This permanently removes the workout and all associated data.
    """
    workout_service = WorkoutService(db)
    
    if not workout_service.delete_workout(user_id, workout_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
