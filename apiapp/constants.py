from enum import IntEnum

class DietType(IntEnum):
    VEGETARIAN = 0
    VEGAN = 1
    PESCATARIAN = 2

class MealType(IntEnum):
    BREAKFAST = 0
    LUNCH = 1
    DINNER = 2

class MealCategory(IntEnum):
    APPETIZER = 0
    MAIN_COURSE = 1
    DESSERT = 2

class DifficultyLevel(IntEnum):
    EASY = 0
    MEDIUM = 1
    HARD = 2

class MeasurementUnit(IntEnum):
    GRAM = 0
    KILOGRAM = 1
    LITER = 2
    TEASPOON = 3
    TABLESPOON = 4
    CUP = 5
