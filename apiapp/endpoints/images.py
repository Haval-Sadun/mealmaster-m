import io
from django.shortcuts import get_object_or_404
from ninja import Router, File, UploadedFile
from typing import List, Optional
from ..models import Image, Recipe
from ..schemas.Image import ImageRead, ImageUpdate
from PIL import Image as PILImage
from ..utils.utils import success, error
from ..schemas.responses import APISuccess, APIError
from django.http import HttpResponse
import base64

router = Router()

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 10 MB max file size


def make_thumbnail(image_bytes, size=(300, 300), fmt="JPEG"):
    """Return thumbnail bytes and content_type"""
    img = PILImage.open(io.BytesIO(image_bytes))
    img.thumbnail(size)
    out = io.BytesIO()
    img.save(out, fmt)
    return out.getvalue(), f"image/{fmt.lower()}"


def image_to_schema(request, img: Image) -> ImageRead:
    """Helper to convert Image model to Pydantic schema with URLs"""
    base_url = request.build_absolute_uri
    return ImageRead(
        id=img.id,
        filename=img.filename,
        size=img.size,
        content_type=img.content_type, 
        url=base_url(f"/api/images/{img.id}/raw/") if img.data else None,
        thumbnail_url=base_url(f"/api/images/{img.id}/thumb/") if img.thumbnail else None,
    )


# List all images
@router.get("/", response={200: APISuccess, 400: APIError})
def list_images(request):
    images = Image.objects.all().order_by("-created_at")
    try:
        schemas = [image_to_schema(request, i).dict() for i in images]
    except Exception as e:
        return error("Error generating image schemas", 500, details=str(e))
    
    return success(schemas, 200)


# List images by recipe
@router.get("/recipes/{recipe_id}/images/", response={200: APISuccess, 404: APIError})
def list_recipe_images(request, recipe_id: int):
    imgs = Image.objects.filter(recipe_id=recipe_id).order_by("-created_at")
    try:
        schemas = [image_to_schema(request, i).dict() for i in imgs]
    except Exception as e:
        return error("Error generating image schemas", 500, details=str(e))
    
    return success(schemas, 200)


# Get image metadata by id
@router.get("/{image_id}", response={200: APISuccess, 404: APIError})
def get_image_metadata(request, image_id: int):
    img = get_object_or_404(Image, id=image_id)
    try:
        schema = image_to_schema(request, img)
    except Exception as e:
        return error("Error generating image schema", 500, details=str(e))
    
    return success(schema.dict(), 200)


# Serve raw image bytes
@router.get("/{image_id}/raw/")
def get_image_raw(request, image_id: int):
    img = get_object_or_404(Image, id=image_id)
    return HttpResponse(img.data, content_type=img.content_type)


# Serve thumbnail bytes
@router.get("/{image_id}/thumb/")
def get_image_thumbnail(request, image_id: int):
    img = get_object_or_404(Image, id=image_id)
    if img.thumbnail:
        return HttpResponse(img.thumbnail, content_type=img.thumbnail_content_type)
    return HttpResponse(status=404)


# Return base64 (optional, mostly for testing or quick frontend previews)
@router.get("/{image_id}/base64/",response={200: APISuccess, 400: APIError})
def get_image_base64(request, image_id: int):
    img = get_object_or_404(Image, id=image_id)
    
    try:
        b64 = base64.b64encode(img.data).decode("ascii")
    except Exception as e:
        return error("Error encoding image to base64", 500, details=str(e))
    
    return success({"id": img.id, "filename": img.filename, "data": f"data:{img.content_type};base64,{b64}", }, 200)


# Upload image
@router.post("/recipes/{recipe_id}/images/", response={200: APISuccess, 400: APIError, 413: APIError})
def upload_image(request, recipe_id: int, file: UploadedFile = File(...)):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    file_bytes = file.file.read()
    size = len(file_bytes)

    if size == 0:
        return error({"error": "Empty file"}, 400)
    if size > MAX_UPLOAD_BYTES:
        return error({"error": "File too large"}, 413)

    try:
        thumb_bytes, thumb_ct = make_thumbnail(file_bytes, size=(400, 400))
    except Exception:
        thumb_bytes, thumb_ct = None, None

    try:
        img = Image.objects.create(
            recipe=recipe,
            filename=file.name,
            content_type=file.content_type or "application/octet-stream",
            size=size,
            data=file_bytes,
            thumbnail=thumb_bytes,
            thumbnail_content_type=thumb_ct,
        )
    except Exception as e:
        return error("Database error while saving image", 500, details=str(e))
    
    schema = image_to_schema(request, img)
    return success(schema.dict(), 201)


# Update image metadata
@router.put("/{image_id}", response={200: APISuccess, 400: APIError, 404: APIError})
def update_image(request, image_id: int, data: ImageUpdate):
    img = get_object_or_404(Image, id=image_id)

    if data.filename is not None:
        img.filename = data.filename

    if data.recipe_id is not None:
        img.recipe = get_object_or_404(Recipe, id=data.recipe_id)
    
    try:
        img.save()
        schema = image_to_schema(request, img)
    except Exception as e:
        return error("Database error while updating image", 500, details=str(e))
    
    return success(schema.dict(), 200)


# Delete image
@router.delete("/{image_id}", response={200: APISuccess, 404: APIError, 500: APIError})
def delete_image(request, image_id: int):
    img = get_object_or_404(Image, id=image_id)
    try:
        img.delete()
    except Exception as e:
        return error("Database error while deleting image", 500, details=str(e))
    
    return success({"message": "Image deleted"}, 200)
