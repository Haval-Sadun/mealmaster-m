from ninja import Schema
from typing import List, Optional
from ..constants import DietType, MealType, MealCategory, DifficultyLevel
from .Ingredient import IngredientCreate, IngredientRead
from .Image import ImageCreate, ImageRead

class RecipeBase(Schema):
    name: str
    description: Optional[str] = None
    instructions: str
    diet_type: DietType
    meal_type: MealType
    meal_category: MealCategory
    preparation_time: int
    cooking_time: int
    difficulty_level: DifficultyLevel
    video_url: Optional[str] = None
    rating: Optional[float] = 0.0
    number_of_servings: Optional[int] = 1

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate] = []
    images: List[ImageCreate] = []

class RecipeRead(RecipeBase):
    id: int
    ingredients: List[IngredientRead] = []
    images: List[ImageRead] = []

    class Config:
        from_attributes = True