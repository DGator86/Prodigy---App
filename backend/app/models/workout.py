"""
Workout, Movement, Split, and ComputedMetrics database models.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base


class Workout(Base):
    """Workout session model."""
    
    __tablename__ = "workouts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    workout_type = Column(String(50), nullable=True)  # Auto-classified type
    template_type = Column(String(50), nullable=False)  # User-selected template
    total_time_seconds = Column(Integer, nullable=False)
    round_count = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    performed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    movements = relationship("Movement", back_populates="workout", cascade="all, delete-orphan")
    splits = relationship("Split", back_populates="workout", cascade="all, delete-orphan")
    metrics = relationship("ComputedMetricsModel", back_populates="workout", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workout {self.id} - {self.name or self.workout_type}>"


class Movement(Base):
    """Movement entry within a workout."""
    
    __tablename__ = "movements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, index=True)
    movement_type = Column(String(50), nullable=False)
    modality = Column(String(20), nullable=False)  # machine, lift, gymnastics
    load_lb = Column(Float, nullable=True)
    reps = Column(Integer, nullable=False)
    calories = Column(Integer, nullable=True)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workout = relationship("Workout", back_populates="movements")
    
    def __repr__(self):
        return f"<Movement {self.movement_type}>"


class Split(Base):
    """Split/round time entry."""
    
    __tablename__ = "splits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    time_seconds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workout = relationship("Workout", back_populates="splits")
    
    def __repr__(self):
        return f"<Split round={self.round_number} time={self.time_seconds}s>"


class ComputedMetricsModel(Base):
    """Computed metrics for a workout."""
    
    __tablename__ = "computed_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Core metrics
    total_ewu = Column(Float, nullable=False)
    density_power_min = Column(Float, nullable=False)
    density_power_sec = Column(Float, nullable=False)
    
    # Optional metrics
    active_power = Column(Float, nullable=True)
    repeatability_drift = Column(Float, nullable=True)
    repeatability_spread = Column(Float, nullable=True)
    repeatability_consistency = Column(Float, nullable=True)
    
    # Modality breakdown
    lift_ewu = Column(Float, nullable=False, default=0)
    machine_ewu = Column(Float, nullable=False, default=0)
    gymnastics_ewu = Column(Float, nullable=False, default=0)
    lift_share = Column(Float, nullable=False)
    machine_share = Column(Float, nullable=False)
    gymnastics_share = Column(Float, nullable=False, default=0)
    
    # Timing
    total_active_seconds = Column(Float, nullable=True)
    rest_seconds = Column(Float, nullable=True)
    
    # Active power per round (stored as JSON)
    per_round_power = Column(JSON, nullable=True)
    
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workout = relationship("Workout", back_populates="metrics")
    
    def __repr__(self):
        return f"<ComputedMetrics workout={self.workout_id} ewu={self.total_ewu}>"
