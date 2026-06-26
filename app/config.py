import os

class Config:
    # Secret Key for session signing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'joms-super-secret-key-18290312')
    
    # Base directory of the project
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # SQLAlchemy Database URI (SQLite used as requested, easily swappable to MySQL)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'joms.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Backup directory configuration
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    
    # Profile photo uploads configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'profile_photos')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB Limit
    
    # Session lifetime and security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # Ensure directories exist
    @classmethod
    def init_app(cls, app):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
