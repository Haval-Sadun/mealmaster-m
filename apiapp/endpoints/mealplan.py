from ninja import Router
from ..schemas.mealplan import MealPlanRead
from ..models import MealPlan
from ..schemas.responses import APISuccess, APIError
from ..utils.utils import success, error
from django.shortcuts import get_object_or_404
from ..models import UserProfile, Recipe, MealPlanEntry
from ..schemas.Recipe import RecipeRead
from ..schemas.mealplan import MealPlanRead, AddRecipeToMealPlan
from ..schemas.mealplanentry import MealPlanEntryRead
from ..auth import KeycloakBearer
from typing import Optional
from django.db.models import F

router = Router(auth=KeycloakBearer())

def mealPlanEntry_to_schema(entry: MealPlanEntry):
    return MealPlanEntryRead.from_orm(entry)

def mealPlan_to_schema(meal_plan:MealPlan):
    return MealPlanRead(
        id=meal_plan.id,
        active=meal_plan.active,
        user_id=str(meal_plan.user_id),
        created_at=str(meal_plan.created_at),
        entries=[MealPlanEntryRead.from_orm(e) for e in meal_plan.entries.all()],
    )

@router.get("/active", response={200: APISuccess, 404: APIError, 500: APIError})
def get_active_meal_plan(request):
    user = request.auth
    try:
        meal_plan, _ = MealPlan.objects.get_or_create(user=user, active=True)
        schema = mealPlan_to_schema(meal_plan)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Failed to get or create active meal plan", 500, str(e))
    
@router.get("/{meal_plan_id}", response={201: APISuccess, 404: APIError, 500: APIError})
def get_meal_plan(request, meal_plan_id: int):
    user = request.auth    
    try:
        meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=user)
        schema = mealPlan_to_schema(request=request, mealPlan=meal_plan)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error in Getting the MealPlan", 404, str(e))

@router.delete("/{meal_plan_id}", response={200: APISuccess, 404: APIError, 500: APIError})
def delete_meal_plan(request, meal_plan_id: int):
    try:
        meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.auth)
        meal_plan.delete()
        return success({"success": True}, 200)
    except Exception as e:
        return error("Error deleting meal plan", 500, details=str(e))
    
@router.post("/add-recipe", response={201: APISuccess, 400: APIError, 500: APIError})
def add_recipe_to_meal_plan(request, data: AddRecipeToMealPlan):
    user: UserProfile = request.auth
    recipe = get_object_or_404(Recipe, id=data.recipe_id)

    # Ensure an active shopping list (meal plan) exists
    meal_plan, _ = MealPlan.objects.get_or_create(user=user, active=True)

    # Link recipe to the shopping list
    meal_plan.recipes.add(recipe)

    # Scale ingredients to number of people
    scale_factor = data.number_of_people / recipe.number_of_servings

    for ingredient in recipe.ingredients.all():
        scaled_qty = ingredient.quantity * scale_factor
        entry, created = MealPlanEntry.objects.get_or_create(
            meal_plan=meal_plan,
            ingredient_name=ingredient.name,
            unit=ingredient.get_measurement_unit_display(),
            defaults={"quantity": scaled_qty, "purchased": False},
        )

        if not created:
            entry.quantity = F("quantity") + scaled_qty
            entry.save(update_fields=["quantity"])
            entry.refresh_from_db()

    return success(
        {"message": "Recipe added to active shopping list", "shopping_list_id": str(meal_plan.id)}, 201
    )

@router.post("/remove-recipe/{recipe_id}", response={201: APISuccess, 400: APIError, 500: APIError})
def remove_recipe_from_shopping_list(request, recipe_id: int):
    user: UserProfile = request.auth
    meal_plan = get_object_or_404(MealPlan, user=user, active=True)
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Remove link between recipe and plan
    meal_plan.recipes.remove(recipe)

    # Decrement ingredient quantities
    for ingredient in recipe.ingredients.all():
        scaled_qty = ingredient.quantity / recipe.number_of_servings
        try:
            entry = MealPlanEntry.objects.get(
                meal_plan=meal_plan,
                ingredient_name=ingredient.name,
                unit=ingredient.get_measurement_unit_display(),
            )
            entry.quantity = F("quantity") - scaled_qty
            entry.save(update_fields=["quantity"])
            entry.refresh_from_db()

            if entry.quantity <= 0:
                entry.delete()
        except MealPlanEntry.DoesNotExist:
            continue

    return success({"message": "Recipe removed from shopping list"}, 201)

@router.patch("/{plan_id}/entries/{entry_id}/increase", response={201: APISuccess, 400: APIError, 500: APIError})
def increase_entry_quantity(request, plan_id: str, entry_id: int, amount: float = 1.0):
    entry = get_object_or_404(MealPlanEntry, id=entry_id, meal_plan_id=plan_id)
    entry.quantity = F("quantity") + amount
    entry.save(update_fields=["quantity"])
    entry.refresh_from_db()

    schema = MealPlanEntryRead.from_orm(entry)
    return success(schema.dict(), 201)


@router.patch("/{plan_id}/entries/{entry_id}/decrease", response={201: APISuccess, 400: APIError, 500: APIError})
def decrease_entry_quantity(request, plan_id: str, entry_id: int, amount: float = 1.0):
    entry = get_object_or_404(MealPlanEntry, id=entry_id, meal_plan_id=plan_id)
    entry.quantity = F("quantity") - amount
    entry.save(update_fields=["quantity"])
    entry.refresh_from_db()

    if entry.quantity <= 0:
        entry.delete()
        return success({"message": "Entry removed (quantity zero)"}, 201)

    schema = MealPlanEntryRead.from_orm(entry)
    return success(schema.dict(), 201)