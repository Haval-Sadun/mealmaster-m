from ninja import Router
from ..schemas.mealplanentry import MealPlanEntryCreate, MealPlanEntryRead, MealPlanEntryUpdate
from ..models import MealPlanEntry, MealPlan
from ..schemas.responses import APISuccess, APIError
from ..utils.utils import success, error
from django.shortcuts import get_object_or_404

router = Router()
@router.post("/{meal_plan_id}",response={201: APISuccess, 400: APIError})
def create_meal_plan_entry(request, meal_plan_id: int, data: MealPlanEntryCreate):
    """
    Create a new meal plan entry for a specific meal plan.
    """
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)

    if not meal_plan.active:
        return error("the meal plan in not Active, create a new one please", 404)
    
    entry = meal_plan.entries.create(**data.dict())
    try:
        schema = MealPlanEntryRead.from_orm(entry)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error creating meal plan entry", 500, details=str(e))

@router.get("/{meal_plan_id}", response={200: APISuccess, 404: APIError})
def list_meal_plan_entries_for_plan(request, meal_plan_id: int):
    """
    List all meal plan entries for a specific meal plan.
    """
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    try:
        entries = meal_plan.entries.all()
        schemas = [MealPlanEntryRead.from_orm(entry).dict() for entry in entries]
        return success(schemas, 200)
    except Exception as e:
        return error("Error listing meal plan entries", 500, details=str(e))

@router.get("/{entry_id}", response={200: APISuccess, 404: APIError})
def get_meal_plan_entry(request, entry_id: int):
    """
    Retrieve a meal plan entry by ID.
    """
    entry = get_object_or_404(MealPlanEntry, id=entry_id)
    try:
        schema = MealPlanEntryRead.from_orm(entry)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error generating meal plan entry schema", 500, details=str(e))
    
@router.put("/{entry_id}", response={200: APISuccess, 404: APIError})
def update_meal_plan_entry(request, entry_id: int, data: MealPlanEntryUpdate):
    """
    Update a meal plan entry by ID.
    """
    entry = get_object_or_404(MealPlanEntry, id=entry_id)
    for attr, value in data.dict().items():
        setattr(entry, attr, value)
    entry.save()
    try:
        schema = MealPlanEntryRead.from_orm(entry)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error updating meal plan entry", 500, details=str(e))