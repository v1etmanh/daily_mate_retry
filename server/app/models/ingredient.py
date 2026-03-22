from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Nutritional scores (0.0 – 1.0 normalized)
    warming_score = Column(Float, default=0.0)       # Tính ấm nóng
    cooling_score = Column(Float, default=0.0)        # Tính mát lạnh
    satiety_score = Column(Float, default=0.0)        # Độ no

    # Nutritional details
    energy_density = Column(Float, default=0.0)       # kcal/100g
    glycemic_index = Column(Float, default=0.0)       # GI value
    carb_g_per100 = Column(Float, default=0.0)        # Carbohydrate (g/100g)
    sodium_density = Column(Float, default=0.0)       # Sodium (mg/100g)
    protein_g_per100 = Column(Float, default=0.0)     # Protein (g/100g)
    fat_g_per100 = Column(Float, default=0.0)         # Fat (g/100g)

    # Constraint flags
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    allergen_tags = Column(String(500), nullable=True)  # comma-separated: "nuts,shellfish"

    # Relationships
    dish_ingredients = relationship("DishIngredient", back_populates="ingredient")

    def __repr__(self):
        return f"<Ingredient id={self.id} name={self.name}>"