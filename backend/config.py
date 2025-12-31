import os
from dotenv import load_dotenv

load_dotenv()

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

class Config:
    # Environment
    ENV = os.environ.get('FLASK_ENV', 'production')  # 'production' or 'development'
    DEBUG = os.environ.get('DEBUG', '0').lower() in ('1', 'true', 'yes')
    TESTING = os.environ.get('TESTING', '0').lower() in ('1', 'true', 'yes')

    # Use DATABASE_URL if provided; otherwise default to a local MySQL connection (change for production)
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Default development MySQL URI - change credentials before deploying
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@127.0.0.1:3306/studenthub')
    # No automatic file creation here; SQLAlchemy will create tables when invoked
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secrets (set securely in production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-secret')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)

    # Debug endpoints and dev fallbacks are explicitly opt-in
    ENABLE_DEBUG_ENDPOINTS = os.environ.get('ENABLE_DEBUG_ENDPOINTS', '0').lower() in ('1','true','yes')
    DEV_SQLITE_FALLBACK = os.environ.get('DEV_SQLITE_FALLBACK', '1').lower() in ('1','true','yes')

    # CORS configuration (comma-separated list of allowed origins). Use a specific origin in production.
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Use absolute path for uploads folder
    upload_folder = os.environ.get('UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(BACKEND_DIR, 'uploads')
    UPLOAD_FOLDER = upload_folder
    # Ensure uploads directory exists
    os.makedirs(upload_folder, exist_ok=True)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
