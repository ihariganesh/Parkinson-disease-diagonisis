"""
Migration script to add cached_recommendations table
"""
import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'parkinson_dev.db')

def add_cache_table():
    """Add cached_recommendations table"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='cached_recommendations'
        """)
        
        if cursor.fetchone():
            print(" cached_recommendations table already exists")
        else:
            # Create cached_recommendations table
            cursor.execute("""
                CREATE TABLE cached_recommendations (
                    id VARCHAR PRIMARY KEY,
                    report_id VARCHAR NOT NULL UNIQUE,
                    recommendations JSON NOT NULL,
                    generation_metadata JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    FOREIGN KEY (report_id) REFERENCES diagnosis_reports(id)
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX idx_cached_recommendations_report_id 
                ON cached_recommendations(report_id)
            """)
            
            conn.commit()
            print(" Successfully created cached_recommendations table")
        
        # Show table info
        cursor.execute("PRAGMA table_info(cached_recommendations)")
        columns = cursor.fetchall()
        print(f"\n cached_recommendations table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f" Error: {e}")
        raise

if __name__ == "__main__":
    print(" Adding cached_recommendations table...")
    add_cache_table()
    print("\n Migration complete!")
