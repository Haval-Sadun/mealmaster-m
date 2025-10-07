# --- Image Schemas ---
from ninja import Schema
from typing import Optional

# Base schema: metadata only (no raw bytes here)
class ImageBase(Schema):
    filename: str
    content_type: str
    size: int

# Schema for creation (upload) – frontend just sends a file,
# so you don't need fields here (the file comes as UploadedFile)
class ImageCreate(Schema):
    pass

# Schema for reading – used when returning to clients
class ImageRead(ImageBase):
    id: int
    url: str
    thumbnail_url: Optional[str] = None  # Optional, if thumbnails exist

    class Config:
        from_attributes = True

        
class ImageUpdate(Schema):
    filename: Optional[str] = None
    recipe_id: Optional[int] = None  
    
    class Config:
        from_attributes = True