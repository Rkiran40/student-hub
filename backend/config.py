import os
from dotenv import load_dotenv

load_dotenv()

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

class Config:
    # Use absolute path for database to avoid path issues
    db_path = os.environ.get('DATABASE_URL')
    if not db_path:
        # Default to backend/studenthub.db with absolute path
        db_path = os.path.join(BACKEND_DIR, 'studenthub.db')
        # Ensure the directory exists
        os.makedirs(BACKEND_DIR, exist_ok=True)
        # Convert to SQLite URI format
        db_path = f'sqlite:///{db_path}'
    elif not db_path.startswith('sqlite:///'):
        # If DATABASE_URL is set but not in URI format, convert it
        db_path = f'sqlite:///{db_path}'
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-me-secret')
    # Use absolute path for uploads folder
    upload_folder = os.environ.get('UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(BACKEND_DIR, 'uploads')
    UPLOAD_FOLDER = upload_folder
    # Ensure uploads directory exists
    os.makedirs(upload_folder, exist_ok=True)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
