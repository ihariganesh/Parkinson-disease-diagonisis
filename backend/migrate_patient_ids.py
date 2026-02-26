"""
Migration script to add patient_id column and generate IDs for existing patients
"""
import sys
sys.path.append('/home/hari/Downloads/parkinson/parkinson-app/backend')

from app.db.database import SessionLocal, engine
from app.db.models import User, UserRole, Base
from sqlalchemy import text

def migrate_patient_ids():
    """Add patient_id column and generate IDs for existing patients"""
    db = SessionLocal()
    
    try:
        print("Starting patient ID migration...")
        
        # Add patient_id column if it doesn't exist
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN patient_id VARCHAR"))
                conn.commit()
                print(" Added patient_id column to users table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("  patient_id column already exists")
            else:
                print(f"  Error adding column: {e}")
        
        # Create unique index if it doesn't exist
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_patient_id ON users(patient_id)"))
                conn.commit()
                print(" Created unique index on patient_id")
        except Exception as e:
            print(f"  Index creation note: {e}")
        
        # Get all patients without patient_id
        patients_without_id = db.query(User).filter(
            User.role == UserRole.PATIENT,
            User.patient_id.is_(None)
        ).all()
        
        print(f"\nFound {len(patients_without_id)} patients without patient IDs")
        
        # Generate patient IDs for existing patients
        for idx, patient in enumerate(patients_without_id, start=1):
            patient_id = f"PID-{idx:06d}"
            
            # Check if ID already exists (shouldn't happen but just in case)
            while db.query(User).filter(User.patient_id == patient_id).first():
                idx += 1
                patient_id = f"PID-{idx:06d}"
            
            patient.patient_id = patient_id
            print(f"   Assigned {patient_id} to {patient.first_name} {patient.last_name} ({patient.email})")
        
        db.commit()
        print(f"\n Successfully assigned patient IDs to {len(patients_without_id)} patients")
        
        # Display all patients with their IDs
        all_patients = db.query(User).filter(User.role == UserRole.PATIENT).all()
        print(f"\n All Patients ({len(all_patients)} total):")
        print("-" * 80)
        for patient in all_patients:
            print(f"   {patient.patient_id or 'NO-ID':<12} | {patient.first_name} {patient.last_name:<20} | {patient.email}")
        print("-" * 80)
        
    except Exception as e:
        db.rollback()
        print(f" Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_patient_ids()
