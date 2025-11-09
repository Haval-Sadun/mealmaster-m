from ninja import Schema
from typing import List, Optional
from .mealplanentry import MealPlanEntryRead
from uuid import UUID
from datetime import datetime



class MealPlanBase(Schema):
    active: Optional[bool] = True


class MealPlanUpdate(MealPlanBase):
    recipe_ids: Optional[List[int]] = None
    # optional: change active status


class MealPlanRead(MealPlanBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    recipes: List[int]  
    entries: List[MealPlanEntryRead]

    class Config:
        from_attributes = True

class AddRecipeToMealPlan(MealPlanBase):
    recipe_id: int
    number_of_people:int