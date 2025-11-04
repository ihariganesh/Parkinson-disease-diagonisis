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
        default_password = "testpass123"  # Default password for all users
        
        print(f"Converting {len(users)} users from bcrypt to PBKDF2...")
        
        for user in users:
            if user.hashed_password.startswith('$2b$'):  # bcrypt hash
                print(f"Converting user: {user.email}")
                user.hashed_password = get_password_hash(default_password)
                
        db.commit()
        print(f"✅ Successfully migrated {len(users)} users")
        print(f"📝 All users now have password: {default_password}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_passwords()