import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import io
try:
    import cloudinary
    import cloudinary.uploader
except Exception:
    cloudinary = None


class CloudStorage:
    def __init__(self, app=None):
        self.app = app
        self.s3_client = None
        self.bucket_name = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.bucket_name = app.config.get('AWS_STORAGE_BUCKET_NAME')
        # Configure Cloudinary if present
        if cloudinary:
            if app.config.get('CLOUDINARY_URL'):
                cloudinary.config(cloudinary_url=app.config['CLOUDINARY_URL'])
            elif app.config.get('CLOUDINARY_CLOUD_NAME') and app.config.get('CLOUDINARY_API_KEY') and app.config.get('CLOUDINARY_API_SECRET'):
                cloudinary.config(
                    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
                    api_key=app.config['CLOUDINARY_API_KEY'],
                    api_secret=app.config['CLOUDINARY_API_SECRET']
                )
        
        # Initialize S3 client only if credentials are available
        if app.config.get('AWS_ACCESS_KEY_ID') and app.config.get('AWS_SECRET_ACCESS_KEY'):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'),
                region_name=app.config.get('AWS_S3_REGION', 'us-east-1'),
                endpoint_url=app.config.get('AWS_S3_ENDPOINT_URL')
            )
    
    def upload_file(self, file, object_name=None):
        """Upload a file to Cloudinary (preferred), S3/Wasabi, or local."""
        # Prefer Cloudinary when configured (best for serverless like Vercel)
        if cloudinary and cloudinary.config().cloud_name:
            url = self._upload_cloudinary(file, object_name)
            if url:
                return url
        
        if not self.s3_client:
            # Fallback to local storage if S3 is not configured
            return self._upload_local(file, object_name)
        
        if object_name is None:
            object_name = secure_filename(file.filename)
        
        try:
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': 'application/pdf'}
            )
            
            # Generate URL
            if self.app.config.get('AWS_S3_ENDPOINT_URL'):
                url = f"{self.app.config['AWS_S3_ENDPOINT_URL']}/{self.bucket_name}/{object_name}"
            else:
                url = f"https://{self.bucket_name}.s3.{self.app.config.get('AWS_S3_REGION', 'us-east-1')}.amazonaws.com/{object_name}"
            
            return url
            
        except NoCredentialsError:
            print("Credentials not available, falling back to local storage")
            return self._upload_local(file, object_name)
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None
    
    def _upload_local(self, file, object_name=None):
        """Fallback local storage method"""
        if object_name is None:
            object_name = secure_filename(file.filename)
        
        upload_dir = os.path.join(self.app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, object_name)
        file.save(file_path)
        
        # Return relative URL for local development
        return f"/uploads/{object_name}"

    def _upload_cloudinary(self, file, object_name=None):
        """Upload PDF to Cloudinary as raw resource and return secure URL."""
        if not cloudinary:
            return None
        if object_name is None:
            object_name = secure_filename(file.filename)
        folder = self.app.config.get('CLOUDINARY_FOLDER', 'tower-docs')
        # Ensure stream pointer at start
        try:
            if hasattr(file, 'stream'):
                file.stream.seek(0)
            else:
                file.seek(0)
            res = cloudinary.uploader.upload(
                file,
                resource_type='raw',
                folder=folder,
                public_id=object_name,
                type='upload',
                access_mode='public',
                overwrite=True,
                use_filename=True,
                unique_filename=False
            )
            return res.get('secure_url') or res.get('url')
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None
    
    def get_pdf_info(self, file):
        """Extract PDF metadata"""
        try:
            # Reset file pointer
            file.seek(0)
            pdf_reader = PdfReader(io.BytesIO(file.read()))
            
            return {
                'page_count': len(pdf_reader.pages),
                'file_size': len(file.getvalue()) if hasattr(file, 'getvalue') else file.content_length
            }
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return {
                'page_count': 0,
                'file_size': 0
            }

# Initialize storage
storage = CloudStorage()
