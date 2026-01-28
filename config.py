import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tower_docs.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Serverless-friendly engine options (no connection pooling across invocations)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'poolclass': NullPool,
    }
    
    # Cloud Storage Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')

    # Cloudinary (preferred on Vercel)
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')  # full URL or set parts below
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    CLOUDINARY_FOLDER = os.environ.get('CLOUDINARY_FOLDER', 'tower-docs')
     
    # Admin Configurations
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # In production, require DATABASE_URL to be set to avoid falling back to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Keep a sentinel so app fails early with a helpful message
        raise RuntimeError('DATABASE_URL is not set. Configure Supabase connection string with ?sslmode=require')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
