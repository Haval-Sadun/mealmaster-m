from django.core.management.base import BaseCommand
from django.utils import timezone
from uuid import uuid4
import random
from ....apiapp.models import UserProfile, Recipe, Ingredient, Image, MealPlan, MealPlanEntry
from ....apiapp.constants import DietType, MealType, MealCategory, DifficultyLevel, MeasurementUnit

class Command(BaseCommand):
    help = "Populate database with sample test data"

    def handle(self, *args, **kwargs):
        # Users
        users = []
        for i in range(10):  # 10 users
            role = "cook" if i % 2 == 0 else "user"
            user = UserProfile.objects.create(
                keycloak_id=uuid4(),
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                role=role
            )
            users.append(user)

        # Recipes
        for user in users:
            for j in range(5):  # 5 recipes per user
                recipe = Recipe.objects.create(
                    name=f"Recipe {j+1} by {user.username}",
                    description="Sample description",
                    instructions="Step 1, Step 2, Step 3",
                    diet_type=random.choice(list(DietType)).value,
                    meal_type=random.choice(list(MealType)).value,
                    meal_category=random.choice(list(MealCategory)).value,
                    preparation_time=random.randint(10, 60),
                    cooking_time=random.randint(15, 90),
                    difficulty_level=random.choice(list(DifficultyLevel)).value,
                    number_of_servings=random.randint(1, 6),
                    cook=user
                )

                # Ingredients
                for k in range(5):  # 5 ingredients per recipe
                    Ingredient.objects.create(
                        name=f"Ingredient {k+1}",
                        quantity=random.randint(1, 10),
                        measurement_unit=random.choice(list(MeasurementUnit)).value,
                        recipe=recipe
                    )

                # Images
                for l in range(2):  # 2 images per recipe
                    Image.objects.create(
                        recipe=recipe,
                        filename=f"image_{j+1}_{l+1}.jpg",
                        size=random.randint(1000, 10000),
                        content_type="image/jpeg"
                    )

        # Meal plans
        for user in users:
            meal_plan = MealPlan.objects.create(
                user=user,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=7),
                active=True
            )

            recipes = Recipe.objects.filter(cook=user)
            for recipe in recipes:
                for ingredient in recipe.ingredients.all():
                    MealPlanEntry.objects.create(
                        meal_plan=meal_plan,
                        ingredient_name=ingredient.name,
                        quantity=ingredient.quantity,
                        unit=ingredient.get_measurement_unit_display(),
                        purchased=random.choice([True, False]),
                        recipe=recipe,
                        number_of_people=random.randint(1, 4),
                        date=timezone.now().date()
                    )

        self.stdout.write(self.style.SUCCESS("Database populated with test data"))
