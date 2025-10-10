from ninja import Schema
from typing import List, Optional
from ..constants import MealType
import datetime

class MealPlanEntryBase(Schema):
    recipe_id: int
    date: datetime.date
    meal_type: MealType
    number_of_people: int = 1

class MealPlanEntryRead(MealPlanEntryBase):
    id: int

    class Config:
        from_attributes  = True

class MealPlanEntryCreate(MealPlanEntryBase):
    pass

class MealPlanEntryUpdate(Schema):
    recipe_id: Optional[int] = None
    date: Optional[datetime.date] = None
    meal_type: Optional[MealType] = None
    number_of_people: Optional[int] = None

    class Config:
        from_attributes = True
