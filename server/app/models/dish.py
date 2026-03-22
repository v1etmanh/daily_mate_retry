from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    # Aggregated vector scores (computed from DishIngredient weights)
    warming_score = Column(Float, default=0.0)   # dish-level warming
    cooling_score = Column(Float, default=0.0)   # dish-level cooling
    satiety_score = Column(Float, default=0.0)   # dish-level satiety

    # Computed nutritional totals (per serving)
    energy_total = Column(Float, default=0.0)        # kcal
    glycemic_load = Column(Float, default=0.0)       # GL
    sodium_total = Column(Float, default=0.0)        # mg

    # Taste profile (0.0 – 1.0 per dimension)
    taste_sweet = Column(Float, default=0.0)
    taste_salty = Column(Float, default=0.0)
    taste_sour = Column(Float, default=0.0)
    taste_bitter = Column(Float, default=0.0)
    taste_umami = Column(Float, default=0.0)
    taste_spicy = Column(Float, default=0.0)

    # Seasonality factor [0,1] — how well this dish fits current season
    seasonality_factor = Column(Float, default=0.5)

    # Relationships
    dish_ingredients = relationship("DishIngredient", back_populates="dish", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dish id={self.id} name={self.name}>"


class DishIngredient(Base):
    """Junction table: Dish M:N Ingredient with quantity info."""
    __tablename__ = "dish_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)

    quantity_g = Column(Float, nullable=False)        # grams in dish
    weight_in_dish = Column(Float, nullable=True)     # qty_i / Σqty (computed)

    # Relationships
    dish = relationship("Dish", back_populates="dish_ingredients")
    ingredient = relationship("Ingredient", back_populates="dish_ingredients")

    def __repr__(self):
        return f"<DishIngredient dish_id={self.dish_id} ingredient_id={self.ingredient_id}>"