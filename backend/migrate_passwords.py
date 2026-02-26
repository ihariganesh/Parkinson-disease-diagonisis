#!/usr/bin/env python3
"""
Migration script to convert bcrypt hashes to PBKDF2 hashes
This will reset all user passwords to a default password
"""

import sys
import os
sys.path.append('/home/hari/Downloads/parkinson/parkinson-app/backend')

from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash

def migrate_passwords():
    """Convert all bcrypt passwords to PBKDF2 with default password"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        # Use an environment variable for the reset password; require explicit configuration
        default_password = os.environ.get("MIGRATION_DEFAULT_PASSWORD")
        if not default_password:
            raise RuntimeError("MIGRATION_DEFAULT_PASSWORD environment variable must be set before running this script")
        
        print(f"Converting {len(users)} users from bcrypt to PBKDF2...")
        
        for user in users:
            if user.hashed_password.startswith('$2b$'):  # bcrypt hash
                user.hashed_password = get_password_hash(default_password)
                
        db.commit()
        print(f" Successfully migrated {len(users)} users")
        print(" All affected users now have a new password set. ")
        print("    Communicate the reset procedure securely (e.g. email reset flow).")
        
    except Exception as e:
        print(f" Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_passwords()