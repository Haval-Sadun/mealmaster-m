from django.shortcuts import get_object_or_404
from ninja.pagination import paginate, PageNumberPagination
from ninja import Router, Schema
from typing import List, TypeVar, Generic

from ..schemas.Image import ImageCreate, ImageRead
from ..schemas.Ingredient import IngredientCreate, IngredientRead
from ..schemas.Recipe import RecipeCreate, RecipeRead
from ..utils.utils import success, error
from ..schemas.responses import APISuccess, APIError
from .images import image_to_schema
from .ingredients import ingredient_to_schemas
from ..models import Recipe

router = Router()

def recipe_to_schema(request, recipe):
    return RecipeRead(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        instructions=recipe.instructions,
        diet_type=recipe.diet_type,
        meal_type=recipe.meal_type,
        meal_category=recipe.meal_category,
        preparation_time=recipe.preparation_time,
        cooking_time=recipe.cooking_time,
        difficulty_level=recipe.difficulty_level,
        video_url=recipe.video_url,
        rating=recipe.rating,
        number_of_servings=recipe.number_of_servings,
        ingredients=[
            IngredientRead.from_orm(i)
            for i in recipe.ingredients.all()
        ],
        images=[ 
            image_to_schema(request, i) for i in recipe.images.all() 
            ]
    )
        #     ImageRead(
        #         id=i.id,
        #         filename=i.filename,
        #         content_type=i.content_type,
        #         size=i.size,
        #         url=request.build_absolute_uri(f"/api/images/{i.id}/raw/"),
        #         thumbnail_url=request.build_absolute_uri(f"/api/images/{i.id}/thumb/") if i.thumbnail else None,
        #     )
        #     for i in recipe.images.all()
        # ]

#------------ Recipe CRUD --------------------
@router.post("/", response={201: APISuccess, 400: APIError, 500: APIError})
def create_recipe(request, data: RecipeCreate):
    try:
        recipe = Recipe.objects.create(**data.dict(exclude={"ingredients", "images"}))

        # Add ingredients
        for ing in data.ingredients:
            recipe.ingredients.create(**ing.dict())

        # Add images
        for img in data.images:
            recipe.images.create(**img.dict())

        # Convert nested objects for response
        recipe.ingredients.all()
        recipe.images.all()
        schema = recipe_to_schema(request, recipe)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error creating recipe", 500, details=str(e))

@router.get("/", response={200: APISuccess, 400: APIError})
def list_recipes(request, page: int = 1, page_size: int = 10):
    try:
        recipes = Recipe.objects.all().prefetch_related("ingredients", "images")
        schemas = [recipe_to_schema(request, r).dict() for r in recipes]

        # Manual pagination
        total = len(schemas)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_schemas = schemas[start:end]

        return success(
            {
                "items": paginated_schemas,  # the current page of items
                "total": total,              # total items
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            status_code=200
        )

    except Exception as e:
        return error("Error generating recipe schemas", 500, details=str(e))

@router.get("/{recipe_id}", response={200: APISuccess, 404: APIError})
def get_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        schema = recipe_to_schema(request, recipe)
    except Exception as e:
        return error("Error generating recipe schema", 500, details=str(e))
    return success(schema.dict(), 200)

# why the DTO is the Create and update
@router.put("/{recipe_id}", response={200: APISuccess, 400: APIError, 404: APIError, 500: APIError})
def update_recipe(request, recipe_id: int, data: RecipeCreate):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        for field, value in data.dict(exlude={"ingredients","images"}).items():
            setattr(recipe, field, value)
        recipe.save()
        schema = recipe_to_schema(request, recipe)
        return success(schema.dict(), 200)
    except Exception as e:
        return error("Error updating recipe", 500, details=str(e))

@router.delete("/{recipe_id}", response={200: APISuccess, 404: APIError, 500: APIError})
def delete_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        recipe.delete()
    except Exception as e:
        return error("Error deleting recipe", 500, details=str(e))
    return success({"success": True}, 200)

#related images
@router.post("/{recipe_id}/images", response={201: APISuccess, 400: APIError, 500: APIError})
def add_image(request, recipe_id: int, image: ImageCreate):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        img = recipe.images.create(**image.dict())
        schema = image_to_schema(request, img)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error adding image", 500, details=str(e))

@router.get("/{recipe_id}/images", response={200: APISuccess, 404: APIError})
def list_images_for_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        schemas = [image_to_schema(request, img).dict() for img in recipe.images.all()]
        return success(schemas, 200)
    except Exception as e:
        return error("Error retrieving images", 500, details=str(e))

#related ingredients
@router.post("/{recipe_id}/ingredients", response={201: APISuccess, 400: APIError, 500: APIError})
def add_ingredient(request, recipe_id: int, ingredient: IngredientCreate):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        ing = recipe.ingredients.create(**ingredient.dict())
        schema = ingredient_to_schemas(request, ing)
        return success(schema.dict(), 201)
    except Exception as e:
        return error("Error adding ingredient", 500, details=str(e))

@router.get("/{recipe_id}/ingredients",response={200: APISuccess, 404: APIError})
def list_ingredients_for_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    try:
        schemas = [ingredient_to_schemas(request, ing).dict() for ing in recipe.ingredients.all()]
        return success(schemas, 200)
    except Exception as e:
        return error("Error retrieving ingredients", 500, details=str(e))

                                                                                                                                                                                                        