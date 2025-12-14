"""
Migration script to add gender column to users table
"""
import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'parkinson_dev.db')

def add_gender_column():
    """Add gender column to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'gender' in columns:
            print("✅ Gender column already exists")
        else:
            # Add gender column
            cursor.execute("ALTER TABLE users ADD COLUMN gender VARCHAR")
            conn.commit()
            print("✅ Successfully added gender column to users table")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"\n📋 Users table now has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    print("🔧 Adding gender column to database...")
    add_gender_column()
    print("\n✅ Migration complete!")
