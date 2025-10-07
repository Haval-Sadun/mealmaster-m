from django.shortcuts import get_object_or_404
from ninja import Router
from typing import List
from ..models import Ingredient, Recipe
from ..schemas.Ingredient import IngredientCreate, IngredientRead
from ..utils.utils import success, error
from ..schemas.responses import APISuccess, APIError
from django.http import HttpResponse

router = Router()

def ingredient_to_schemas(request, ing: Ingredient) ->  IngredientRead:
    """Helper to convert related ingredients to list of schemas"""
    return IngredientRead.from_orm(ing) 

# Get a single ingredient
@router.get("/{ingredient_id}", response={200: APISuccess, 404: APIError})
def get_ingredient(request, ingredient_id: int):
    try:
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        # Convert to schema
        schema = ingredient_to_schemas(request, ingredient)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Ingredient not found", 404, details=str(e))
    
# List all ingredients or filter by recipe
@router.get("/", response={200: APISuccess, 400: APIError})
def list_ingredients(request, recipe_id: int = None):
    try:
        if recipe_id:
            ingredients = Ingredient.objects.filter(recipe_id=recipe_id)
        else:
            ingredients = Ingredient.objects.all()
        schemas = [ingredient_to_schemas(request, i).dict() for i in ingredients]
        return success(schemas, 200)
    except Exception as e:
        return error("Error retrieving ingredients", 500, details=str(e))

# Create a new ingredient for a recipe
@router.post("/recipes/{recipe_id}", response={201: APISuccess, 400: APIError, 500: APIError})
def create_ingredient(request, recipe_id: int, data: IngredientCreate):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        ingredient = Ingredient.objects.create(recipe=recipe, **data.dict())
        schema = ingredient_to_schemas(request, ingredient)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error creating ingredient", 500, details=str(e))

# Update an existing ingredient
@router.put("/{ingredient_id}", response={200: APISuccess, 400: APIError, 404: APIError, 500: APIError})
def update_ingredient(request, ingredient_id: int, data: IngredientCreate):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    try:
        for field, value in data.dict().items():
            setattr(ingredient, field, value)
        ingredient.save()
        schema = ingredient_to_schemas(request, ingredient)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error updating ingredient", 500, details=str(e))
    

# Delete an ingredient
@router.delete("/{ingredient_id}", response={200: APISuccess, 404: APIError, 500: APIError})
def delete_ingredient(request, ingredient_id: int):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    try:
        ingredient.delete()
        return success({"message": "Ingredient deleted"}, 200)
    except Exception as e:
        return error("Error deleting ingredient", 500, details=str(e))

