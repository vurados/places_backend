from io import BytesIO
from PIL import Image
import secrets
from app.services.minio_service import minio_client

async def process_and_upload_image(file, user_id: str):
    # Generate secure random filename
    file_extension = file.filename.split('.')[-1]
    random_hex = secrets.token_hex(8)
    filename = f"{user_id}_{random_hex}.{file_extension}"
    
    # Read and process image
    image = Image.open(BytesIO(await file.read()))
    
    # Create thumbnail
    thumbnail = image.copy()
    thumbnail.thumbnail((300, 300))
    
    # Save images to bytes
    original_bytes = BytesIO()
    thumbnail_bytes = BytesIO()
    
    image.save(original_bytes, format=image.format)
    thumbnail.save(thumbnail_bytes, format=image.format)
    
    # Upload to MinIO
    original_bytes.seek(0)
    thumbnail_bytes.seek(0)
    
    original_filename, original_url = await minio_client.upload_image(
        original_bytes, filename, file.content_type
    )
    
    thumb_filename, thumb_url = await minio_client.upload_image(
        thumbnail_bytes, f"thumb_{filename}", file.content_type
    )
    
    return {
        "original_filename": original_filename,
        "original_url": original_url,
        "thumbnail_filename": thumb_filename,
        "thumbnail_url": thumb_url
    }