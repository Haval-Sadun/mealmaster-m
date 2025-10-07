from ninja import NinjaAPI
from .endpoints.recipes import router as recipe_router
from .endpoints.ingredients import router as ingredient_router
from .endpoints.images import router as image_router
from .utils.exceptions import global_exception_handler

api = NinjaAPI(
    title="Recipe API",
    version="1.0.0",
    description="Backend API for the Recipe app",
)

# Register global exception handler
api.add_exception_handler(Exception, global_exception_handler)

api.add_router("/recipes/", recipe_router, tags=["Recipes"])
api.add_router("/ingredients/", ingredient_router, tags=["Ingredients"])
api.add_router("/images/", image_router, tags=["Images"])

# Optional: Add a health check route
@api.get("/health", tags=["System"])
def health_check(request):
    return {"status": "ok", "message": "API running"}
