from ninja import Router
from ..constants import DietType, MealType, MealCategory, DifficultyLevel, MeasurementUnit

router = Router()

@router.get("/")
def list_enums(request):
    """List available enums"""
    return {
        "diet_type": [{"value": e.value, "label": e.name.capitalize()} for e in DietType],
        "meal_type": [{"value": e.value, "label": e.name.capitalize()} for e in MealType],
        "meal_category": [{"value": e.value, "label": e.name.capitalize()} for e in MealCategory],
        "difficulty_level": [{"value": e.value, "label": e.name.capitalize()} for e in DifficultyLevel],
        "measurement_unit": [{"value": e.value, "label": e.name.capitalize()} for e in MeasurementUnit],
    }