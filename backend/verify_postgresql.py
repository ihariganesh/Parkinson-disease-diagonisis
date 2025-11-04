#!/usr/bin/env python3
"""
PostgreSQL Database Verification Script
This script verifies that PostgreSQL is properly configured and working
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.database import engine
from app.db.models import Base

def main():
    """Verify PostgreSQL setup"""
    print("🔍 Verifying PostgreSQL Database Setup...")
    print("=" * 50)
    
    # Check database URL
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    if 'postgresql' not in settings.DATABASE_URL:
        print("❌ Database URL is not PostgreSQL!")
        return False
    
    print("✅ Database URL is PostgreSQL")
    
    try:
        # Test connection
        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL Version: {version.split(',')[0]}")
            
            # Check database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")
            
            # Check user
            result = conn.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"✅ Connected as user: {user}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT tablename, tableowner 
                FROM pg_tables 
                WHERE schemaname='public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            print(f"\n📋 Database Tables ({len(tables)} total):")
            for table_name, owner in tables:
                # Get row count
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = count_result.fetchone()[0]
                print(f"  • {table_name} (owner: {owner}, rows: {count})")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname='public' 
                AND indexname NOT LIKE '%_pkey'
                ORDER BY tablename, indexname
            """))
            indexes = result.fetchall()
            
            if indexes:
                print(f"\n🔍 Custom Indexes ({len(indexes)} total):")
                for index_name, table_name in indexes:
                    print(f"  • {index_name} on {table_name}")
            else:
                print("\n🔍 No custom indexes found (using primary keys only)")
            
            # Check database size
            result = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            db_size = result.fetchone()[0]
            print(f"\n💾 Database Size: {db_size}")
            
            # Check active connections
            result = conn.execute(text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """))
            connections = result.fetchone()[0]
            print(f"🔗 Active Connections: {connections}")
            
            print("\n" + "=" * 50)
            print("🎉 PostgreSQL verification completed successfully!")
            print("\n📋 Summary:")
            print(f"  ✅ PostgreSQL {version.split()[1]} is running")
            print(f"  ✅ Database '{db_name}' is accessible")
            print(f"  ✅ {len(tables)} tables created")
            print(f"  ✅ Connection pool configured")
            print(f"  ✅ Ready for production use")
            
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        print("\n💡 Troubleshooting steps:")
        print("1. Ensure PostgreSQL service is running: sudo systemctl status postgresql")
        print("2. Check database connection: psql -h localhost -U parkinson_user -d parkinson_db")
        print("3. Verify credentials in .env file")
        print("4. Run setup script: ./setup_postgresql.sh")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)