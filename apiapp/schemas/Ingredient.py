from ninja import Schema
from typing import  Optional
from apiapp.constants import MeasurementUnit

# --- Ingredient Schemas ---
class IngredientBase(Schema):
    name: str
    category: Optional[str] = None
    quantity: int
    measurement_unit: MeasurementUnit

class IngredientCreate(IngredientBase):
    pass

class IngredientRead(IngredientBase):
    id: int

    class Config:
        from_attributes  = True
