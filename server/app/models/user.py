import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class ActivityLevelEnum(str, enum.Enum):
    sedentary = "sedentary"          # Ít vận động
    lightly_active = "lightly_active"  # Nhẹ (1-3 ngày/tuần)
    moderately_active = "moderately_active"  # Vừa (3-5 ngày/tuần)
    very_active = "very_active"      # Nhiều (6-7 ngày/tuần)
    extra_active = "extra_active"    # Rất nhiều (2 lần/ngày)


class DietTypeEnum(str, enum.Enum):
    omnivore = "omnivore"
    vegetarian = "vegetarian"
    vegan = "vegan"
    pescatarian = "pescatarian"
    keto = "keto"
    halal = "halal"
    kosher = "kosher"


class PersonalInput(Base):
    """Stored user profile — maps to PersonalInput entity."""
    __tablename__ = "personal_inputs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, unique=True, index=True)  # external auth ID

    # Demographics
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    activity_level = Column(Enum(ActivityLevelEnum), nullable=False, default=ActivityLevelEnum.sedentary)
    diet_type = Column(Enum(DietTypeEnum), nullable=False, default=DietTypeEnum.omnivore)

    # Disease flags
    has_diabetes = Column(Boolean, default=False)
    has_hypertension = Column(Boolean, default=False)
    has_gout = Column(Boolean, default=False)
    has_kidney_disease = Column(Boolean, default=False)

    # Allergy tags (comma-separated ingredient IDs or tag names)
    allergy_tags = Column(String(500), nullable=True)

    # Taste preference weights (0.0 – 1.0)
    pref_sweet = Column(Float, default=0.5)
    pref_salty = Column(Float, default=0.5)
    pref_sour = Column(Float, default=0.5)
    pref_bitter = Column(Float, default=0.5)
    pref_umami = Column(Float, default=0.5)
    pref_spicy = Column(Float, default=0.5)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PersonalInput id={self.id} user_id={self.user_id}>"