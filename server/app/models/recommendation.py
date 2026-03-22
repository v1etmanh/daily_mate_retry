from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class RecommendationResult(Base):
    """Snapshot of a full recommendation pipeline run."""
    __tablename__ = "recommendation_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    session_id = Column(String(128), nullable=True, index=True)

    # Input snapshots (stored as JSON for auditability)
    weather_snapshot = Column(JSON, nullable=True)    # WeatherVector at time of request
    location_snapshot = Column(JSON, nullable=True)   # LocationVector
    personal_snapshot = Column(JSON, nullable=True)   # PersonalVector
    demand_snapshot = Column(JSON, nullable=True)     # PhysiologicalDemand

    # Explanation text (assembled from ExplanationFragments)
    explanation_text = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ranked_dishes = relationship("RankedDish", back_populates="recommendation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RecommendationResult id={self.id} user_id={self.user_id}>"


class RankedDish(Base):
    """A single dish entry in a RecommendationResult, with scoring breakdown."""
    __tablename__ = "ranked_dishes"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation_results.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)

    rank = Column(Integer, nullable=False)                  # 1-based ranking
    base_score = Column(Float, default=0.0)                 # dot-product Score(dish)
    taste_bonus = Column(Float, default=0.0)                # 0.15 × taste_bonus
    seasonality_bonus = Column(Float, default=0.0)          # 0.10 × seasonality_factor
    final_score = Column(Float, default=0.0)                # FinalScore = 0.75×score + taste + season

    # Detailed score breakdown per demand dimension (stored as JSON)
    score_breakdown = Column(JSON, nullable=True)

    # Suggested substitutions if some ingredients are unavailable (list of ingredient IDs)
    substitutions = Column(JSON, nullable=True)

    # Relationships
    recommendation = relationship("RecommendationResult", back_populates="ranked_dishes")
    dish = relationship("Dish")

    def __repr__(self):
        return f"<RankedDish rank={self.rank} dish_id={self.dish_id} score={self.final_score}>"