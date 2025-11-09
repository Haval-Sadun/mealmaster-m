from ninja import Schema
from typing import List, Optional
from ..constants import MealType
from uuid import UUID


class MealPlanEntryBase(Schema):
    ingredient_name: str
    quantity: float
    unit: str
    purchased: Optional[bool] = False


class MealPlanEntryCreate(MealPlanEntryBase):
    pass  # For creation, all fields except ID and FK


class MealPlanEntryUpdate(Schema):
    quantity: Optional[float]
    purchased: Optional[bool]


class MealPlanEntryRead(MealPlanEntryBase):
    id: int
    shopping_list_id: UUID

    class Config:
        from_attributes = True
