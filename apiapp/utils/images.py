# utils/images.py
from PIL import Image as PILImage
import io
from django.utils import timezone
from ..models import Image
from ..schemas.Image import ImageRead

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 10 MB

def make_thumbnail(image_bytes, size=(400, 400), fmt="JPEG"):
    """Generate a thumbnail from raw image bytes"""
    img = PILImage.open(io.BytesIO(image_bytes))
    img.thumbnail(size)
    out = io.BytesIO()
    img.save(out, fmt)
    return out.getvalue(), f"image/{fmt.lower()}"

def save_image_to_recipe(recipe, *, filename, content_type, file_bytes):
    """Core logic for saving image bytes and generating thumbnail"""
    thumb_bytes, thumb_ct = None, None
    try:
        thumb_bytes, thumb_ct = make_thumbnail(file_bytes)
    except Exception:
        pass

    return Image.objects.create(
        recipe=recipe,
        filename=filename,
        content_type=content_type or "application/octet-stream",
        size=len(file_bytes),
        data=file_bytes,
        thumbnail=thumb_bytes,
        thumbnail_content_type=thumb_ct,
        created_at=timezone.now(),
    )

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