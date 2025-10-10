from django.db import models
from .constants import DietType, MealType, MealCategory, DifficultyLevel, MeasurementUnit
from django.utils import timezone

def enum_choices(enum_cls):
    return [(member.value, member.name.capitalize().replace("_", " ")) for member in enum_cls]

# Recipe 
class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    diet_type = models.IntegerField(choices=enum_choices(DietType))
    meal_type =  models.IntegerField(choices=enum_choices(MealType))
    meal_category = models.IntegerField(choices=enum_choices( MealCategory))
    preparation_time = models.PositiveIntegerField()  # in minutes
    cooking_time = models.PositiveIntegerField()      # in minutes
    difficulty_level = models.IntegerField(choices=enum_choices(DifficultyLevel))
    video_url = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0)
    number_of_servings = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

   # Optional helpers — cleaner and ORM-friendly
    def add_image(self, image_name, image_url):
        return self.images.create(image_name=image_name, image_url=image_url)

    def add_ingredient(self, name, quantity, measurement_unit, category=""):
        return self.ingredients.create(
            name=name,
            quantity=quantity,
            measurement_unit=measurement_unit,
            category=category,
        )

    def __eq__(self, other):
        return isinstance(other, Recipe) and self.name == other.name

    def __hash__(self):
        return hash((self.name, self.instructions, self.preparation_time))
    

#Ingredients
class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)  # category can be optional
    quantity = models.PositiveIntegerField()
    measurement_unit = models.IntegerField(choices=enum_choices(MeasurementUnit))  # assuming enum with choices

    # Foreign key relation to Recipe
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} {self.get_measurement_unit_display()} of {self.name}"

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash((self.name, self.quantity, self.recipe_id, self.category))

# Images
class Image(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="images", on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, default="application/octet-stream")
    size = models.PositiveIntegerField(default=0)
    data = models.BinaryField(null=True, blank=True)
    thumbnail = models.BinaryField(null=True, blank=True)
    thumbnail_content_type = models.CharField(max_length=100, null=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.filename} ({self.size} bytes)"
    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        return self.image_name == other.image_name and self.image_url == other.image_url

    def __hash__(self):
        return hash((self.image_name, self.image_url, self.recipe_id))


class MealPlan(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)  # Uncomment if User model is available  
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"plan for {self.start_date} → {self.end_date}"
    
class MealPlanEntry(models.Model):
    meal_plan = models.ForeignKey(MealPlan, related_name='entries', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.IntegerField(choices=enum_choices(MealType))
    number_of_people = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.recipe.name} on {self.date} ({self.get_meal_type_display()})"