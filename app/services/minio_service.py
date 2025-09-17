from minio import Minio
from minio.error import S3Error
import uuid
from core.config import settings
import os

class MinioClient:
    def __init__(self):
        if os.environ.get("TESTING") == "True":
            self.client = None
            return

        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        
        # Create bucket if not exists
        self._create_bucket()
    
    def _create_bucket(self):
        if self.client is None:
            return
        
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Bucket {self.bucket_name} created successfully")
        except S3Error as err:
            print(f"Error creating bucket: {err}")
    
    async def upload_image(self, file_data, file_name, content_type):
        if self.client is None:
            # В тестовом режиме возвращаем заглушку
            unique_filename = f"test_{uuid.uuid4()}.{file_name.split('.')[-1]}"
            return unique_filename, f"http://test-minio/{unique_filename}"
        
        try:
            # Generate unique filename
            file_extension = file_name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                unique_filename,
                file_data,
                length=-1,
                part_size=10*1024*1024,
                content_type=content_type
            )
            
            # Generate URL
            url = self.client.presigned_get_object(
                self.bucket_name, 
                unique_filename
            )
            
            return unique_filename, url.split('?')[0]  # Return filename and base URL
            
        except S3Error as err:
            print(f"Error uploading file: {err}")
            raise
    
    async def delete_image(self, file_name):
        try:
            self.client.remove_object(self.bucket_name, file_name)
        except S3Error as err:
            print(f"Error deleting file: {err}")
            raise

# Create global MinIO client instance
minio_client = MinioClient()