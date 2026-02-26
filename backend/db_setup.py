#!/usr/bin/env python3
"""
Database setup script for Parkinson's Detection App
This script creates the database tables using SQLAlchemy with PostgreSQL
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.db.models import Base
from app.core.config import settings

def create_tables(database_url):
    """Create all database tables"""
    try:
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        print(" Created all database tables")
        
        # List created tables
        inspector = create_engine(database_url).connect()
        result = inspector.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        
        tables = [row[0] for row in result.fetchall()]
        print(f" Created tables: {', '.join(tables)}")
        inspector.close()
        
        return True
    except Exception as e:
        print(f" Error creating tables: {e}")
        return False

def test_database_connection(database_url):
    """Test PostgreSQL database connection"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f" PostgreSQL connection successful: {version}")
        return True
    except Exception as e:
        print(f" PostgreSQL connection failed: {e}")
        print(" Make sure PostgreSQL is running and credentials are correct")
        print(" Run: ./setup_postgresql.sh to set up PostgreSQL")
        return False

def main():
    """Main setup function"""
    print(" Setting up Parkinson's Detection App Database with PostgreSQL...")
    
    # Use PostgreSQL only
    database_url = settings.DATABASE_URL
    
    if 'postgresql' not in database_url:
        print(" DATABASE_URL must be a PostgreSQL connection string!")
        print(" Please update your .env file with PostgreSQL connection details")
        print(" Run: ./setup_postgresql.sh to set up PostgreSQL")
        return False
    
    print(" Setting up PostgreSQL database...")
    
    # Test connection
    if not test_database_connection(database_url):
        print(" Could not establish PostgreSQL connection")
        print(" Please ensure PostgreSQL is running and credentials are correct")
        print(" Run: ./setup_postgresql.sh to set up PostgreSQL")
        return False
    
    # Create tables
    tables_success = create_tables(database_url)
    if not tables_success:
        return False
    
    print("\n PostgreSQL database setup completed successfully!")
    print(f" Database URL: {database_url}")
    print("\n Next steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Start the backend server: uvicorn app.main:app --reload")
    print("3. The API will be available at: http://localhost:8000")
    print("4. API documentation at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)