import enum
from sqlalchemy import Column, Integer, String, Text, Enum
from app.models.base import Base


class FragmentTypeEnum(str, enum.Enum):
    context = "context"       # Giải thích về thời tiết / vị trí
    dish = "dish"             # Giải thích lý do gợi ý món ăn
    constraint = "constraint" # Giải thích về ràng buộc sức khỏe


class ExplanationFragment(Base):
    """
    Template-based explanation fragment used to compose recommendation explanations.
    Fragments are selected and assembled by explanation_service based on context.
    """
    __tablename__ = "explanation_fragments"

    id = Column(Integer, primary_key=True, index=True)

    fragment_type = Column(Enum(FragmentTypeEnum), nullable=False, index=True)

    # e.g. "high_heat", "cold_weather", "diabetic_constraint", "high_satiety_dish"
    condition_key = Column(String(128), nullable=False, index=True)

    # Template string with placeholders, e.g. "Trời nóng {temp}°C, nên ăn đồ mát."
    text_template = Column(Text, nullable=False)

    # Variant index for A/B variety (0, 1, 2, ...)
    variant_index = Column(Integer, default=0)

    # Language code: "vi", "en", etc.
    language = Column(String(8), nullable=False, default="vi")

    def __repr__(self):
        return (
            f"<ExplanationFragment type={self.fragment_type} "
            f"key={self.condition_key} variant={self.variant_index} lang={self.language}>"
        )