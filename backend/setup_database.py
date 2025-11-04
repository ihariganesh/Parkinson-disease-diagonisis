#!/usr/bin/env python3
"""
Database setup script for Parkinson's Detection App
This script creates the database tables using SQLAlchemy
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from app.db.database import engine, Base
from app.db.models import User, Patient, Doctor, MedicalData, AnalysisResult, DiagnosisReport, LifestyleSuggestion
from app.core.config import settings


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def seed_sample_data():
    """Add sample data to the database"""
    from sqlalchemy.orm import sessionmaker
    from app.core.security import get_password_hash
    import uuid
    from datetime import datetime
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("📊 Sample data already exists, skipping...")
            return True
            
        print("Seeding sample data...")
        
        # Create sample users
        sample_users = [
            {
                "id": str(uuid.uuid4()),
                "email": "doctor@example.com",
                "hashed_password": get_password_hash("doctor123"),
                "first_name": "Dr. Sarah",
                "last_name": "Johnson",
                "role": "doctor",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "email": "patient@example.com", 
                "hashed_password": get_password_hash("patient123"),
                "first_name": "John",
                "last_name": "Doe",
                "role": "patient",
                "date_of_birth": datetime(1960, 5, 15),
                "is_active": True
            }
        ]
        
        for user_data in sample_users:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print("✅ Sample data seeded successfully!")
        
        # Print login credentials
        print("\n🔑 Sample Login Credentials:")
        print("Doctor: doctor@example.com / doctor123")
        print("Patient: patient@example.com / patient123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function to initialize the database"""
    print("🏥 Parkinson's Detection App - Database Setup")
    print("=" * 50)
    
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    # Ask user if they want sample data
    while True:
        choice = input("\n❓ Would you like to add sample data? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            seed_sample_data()
            break
        elif choice in ['n', 'no']:
            print("Skipping sample data...")
            break
        else:
            print("Please enter 'y' or 'n'")
    
    print("\n🎉 Database setup completed!")
    print("You can now start the FastAPI server with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()