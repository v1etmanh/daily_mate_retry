import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from app.models.base import Base


class ActionTypeEnum(str, enum.Enum):
    view = "view"           # Người dùng xem dish
    click = "click"         # Người dùng click vào dish
    save = "save"           # Người dùng lưu dish
    skip = "skip"           # Người dùng bỏ qua
    rate = "rate"           # Người dùng đánh giá (kèm rating)
    order = "order"         # Người dùng đặt món


class UserFeedback(Base):
    """Records a single user interaction/feedback on a recommended dish."""
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation_results.id", ondelete="SET NULL"), nullable=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)

    action_type = Column(Enum(ActionTypeEnum), nullable=False)
    rating = Column(Float, nullable=True)          # 1.0 – 5.0; only when action_type = rate
    time_to_action_sec = Column(Float, nullable=True)  # seconds from recommendation to action

    # Snapshot of context at time of feedback
    context_snapshot = Column(JSON, nullable=True)     # weather/location/demand at that moment

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserFeedback id={self.id} user_id={self.user_id} action={self.action_type}>"


class UserPreferenceModel(Base):
    """Learned taste preference model per user — updated via EMA from feedback."""
    __tablename__ = "user_preference_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, unique=True, index=True)

    # Learned taste weights (EMA-updated, 0.0 – 1.0)
    learned_sweet = Column(Float, default=0.5)
    learned_salty = Column(Float, default=0.5)
    learned_sour = Column(Float, default=0.5)
    learned_bitter = Column(Float, default=0.5)
    learned_umami = Column(Float, default=0.5)
    learned_spicy = Column(Float, default=0.5)

    # Ingredient affinity map: {ingredient_id: delta_score}
    ingredient_affinity = Column(JSON, nullable=True)

    # Confidence: number of rated interactions; activate learned weight when >= 20
    confidence_score = Column(Integer, default=0)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserPreferenceModel user_id={self.user_id} confidence={self.confidence_score}>"