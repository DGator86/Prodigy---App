"""
Domain scores and distribution models.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db.database import Base


class DomainScoreModel(Base):
    """Domain score for athlete completeness radar."""
    
    __tablename__ = "domain_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(50), nullable=False)  # strength_output, monostructural_output, etc.
    raw_value = Column(Float, nullable=True)
    normalized_score = Column(Float, nullable=True)
    sample_count = Column(Integer, default=0)
    confidence = Column(String(20), default="no_data")  # no_data, low, medium, high
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on user + domain
    __table_args__ = (
        UniqueConstraint('user_id', 'domain', name='uq_user_domain'),
    )
    
    # Relationships
    user = relationship("User", back_populates="domain_scores")
    
    def __repr__(self):
        return f"<DomainScore {self.domain}: {self.normalized_score}>"


class DistributionModel(Base):
    """Distribution data for percentile normalization."""
    
    __tablename__ = "distributions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_type = Column(String(50), nullable=False)
    metric_name = Column(String(50), nullable=False)
    values_json = Column(JSON, default=list)  # [{value, workout_id, performed_at}, ...]
    window_days = Column(Integer, default=180)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'workout_type', 'metric_name', name='uq_distribution'),
    )
    
    # Relationships
    user = relationship("User", back_populates="distributions")
    
    def __repr__(self):
        return f"<Distribution {self.workout_type}/{self.metric_name}>"
