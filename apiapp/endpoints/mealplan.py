from ninja import Router
from ..schemas.mealplan import MealPlanCreate, MealPlanRead, MealPlanUpdate
from ..models import MealPlan
from ..schemas.responses import APISuccess, APIError
from ..utils.utils import success, error
from django.shortcuts import get_object_or_404

router = Router()

@router.post("/", response={201: APISuccess, 400: APIError})
def create_meal_plan(request, data: MealPlanCreate):
    """
    Create a new meal plan.
    """
    meal_plan = MealPlan.objects.create(**data.dict(exclude={"entries"}))
    #user = request.user
    if(data.entries):
        for entry in data.entries:
            meal_plan.entries.create(**entry.dict())
            
    meal_plan.entries.all()  # Ensure entries are loaded
    try:
        schema = MealPlanRead.from_orm(meal_plan)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error creating meal plan", 500, details=str(e))
    
@router.get("/{meal_plan_id}", response={200: APISuccess, 404: APIError})
def get_meal_plan(request, meal_plan_id: int):
    """
    Retrieve a meal plan by ID.
    """
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    try:
        schema = MealPlanRead.from_orm(meal_plan)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error generating meal plan schema", 500, details=str(e))

@router.get("/active", response={200: APISuccess, 404: APIError})
def get_active_meal_plan(request):
    """
    Retrieve the active meal plan.
    """
    try:
        meal_plan = MealPlan.objects.filter(active=True).prefetch_related("entries").first()
        if not meal_plan:
            return error("No active meal plan found, create a new one please", 404)
        schema = MealPlanRead.from_orm(meal_plan)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error retrieving active meal plan", 500, details=str(e))

@router.get("/", response={200: APISuccess, 400: APIError})
def list_meal_plans(request):
    """
    List all meal plans.
    """
    try:
        meal_plans = MealPlan.objects.all().prefetch_related("entries")
        schemas = [MealPlanRead.from_orm(mp).dict() for mp in meal_plans]
        return success(schemas, 200)
    except Exception as e:
        return error("Error generating meal plan schemas", 500, details=str(e))

@router.put("/{meal_plan_id}", response={200: APISuccess, 400: APIError, 404: APIError})
def update_meal_plan(request, meal_plan_id: int, data: MealPlanUpdate):
    """
    Update an existing meal plan.
    """
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    try:
        for field, value in data.dict(exclude_unset=True).items():
            setattr(meal_plan, field, value)
        meal_plan.save()
        
        meal_plan.entries.all()  # Ensure entries are loaded
        schema = MealPlanRead.from_orm(meal_plan)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error updating meal plan", 500, details=str(e))
    
@router.delete("/{meal_plan_id}", response={200: APISuccess, 404: APIError, 500: APIError})
def delete_meal_plan(request, meal_plan_id: int):
    """
    Delete a meal plan by ID.
    """
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    try:
        meal_plan.delete()
        return success({"success": True}, 200)
    except Exception as e:
        return error("Error deleting meal plan", 500, details=str(e))
    

