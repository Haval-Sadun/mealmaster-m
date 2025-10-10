from ninja import Schema
from datetime import date
from typing import List, Optional
from .mealplanentry import MealPlanEntryRead, MealPlanEntryCreate

class MealPlanBase(Schema):
    start_date: date
    end_date: date
    active: Optional[bool] = True

class MealPlanRead(MealPlanBase):
    id: int
    entries: List[MealPlanEntryRead]

    class Config:
        from_attributes = True

class MealPlanCreate(MealPlanBase):
    entries: Optional[List[MealPlanEntryCreate]] = None

class MealPlanUpdate(Schema):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    active: Optional[bool] = None

    class Config:
        from_attributes = True
