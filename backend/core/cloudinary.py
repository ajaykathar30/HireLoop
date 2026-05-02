import cloudinary
import cloudinary.uploader
import asyncio
from core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_file(file_content: bytes, folder_path: str, public_id: str = None):
    """
    Uploads a file to Cloudinary.
    folder_path: e.g., "HireLoop/Resume" or "HireLoop/CompanyLogo"
    """
    def _upload():
        return cloudinary.uploader.upload(
            file_content,
            folder=folder_path,
            public_id=public_id,
            resource_type="auto"
        )
    upload_result = await asyncio.to_thread(_upload)
    return upload_result.get("secure_url")
