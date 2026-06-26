import os
import shutil
from datetime import datetime
from flask import current_app

class BackupService:
    """Manages database snapshots and archival for system backups."""
    
    @staticmethod
    def create_backup():
        """Creates a timestamped snapshot copy of the SQLite database."""
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        backup_dir = current_app.config['BACKUP_DIR']
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at {db_path} to perform backup.")
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"joms_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Perform safe copy
        shutil.copy2(db_path, backup_path)
        return backup_filename

    @staticmethod
    def list_backups():
        """Lists all existing backup files sorted by modified time descending."""
        backup_dir = current_app.config['BACKUP_DIR']
        if not os.path.exists(backup_dir):
            return []
            
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("joms_backup_") and filename.endswith(".db"):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size_kb': round(stat.st_size / 1024, 2),
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        # Sort by creation date descending
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

    @staticmethod
    def delete_backup(filename):
        """Deletes a specific database backup file securely."""
        backup_dir = current_app.config['BACKUP_DIR']
        # Secure filename check to prevent traversal directory attacks
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(backup_dir, safe_filename)
        
        if os.path.exists(filepath) and safe_filename.startswith("joms_backup_") and safe_filename.endswith(".db"):
            os.remove(filepath)
            return True
        return False
