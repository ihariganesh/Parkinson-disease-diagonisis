from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import traceback

from app.db.database import get_db
from app.db.models import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role.value,
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "phone_number": current_user.phone_number,
            "address_street": current_user.address_street if hasattr(current_user, 'address_street') else None,
            "address_city": current_user.address_city if hasattr(current_user, 'address_city') else None,
            "address_state": current_user.address_state if hasattr(current_user, 'address_state') else None,
            "address_zip": current_user.address_zip if hasattr(current_user, 'address_zip') else None,
            "address_country": current_user.address_country if hasattr(current_user, 'address_country') else None,
            "emergency_contact_name": current_user.emergency_contact_name if hasattr(current_user, 'emergency_contact_name') else None,
            "emergency_contact_phone": current_user.emergency_contact_phone if hasattr(current_user, 'emergency_contact_phone') else None,
            "emergency_contact_relationship": current_user.emergency_contact_relationship if hasattr(current_user, 'emergency_contact_relationship') else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        }
    except Exception as e:
        print(f"Error fetching profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    try:
        print(f"Updating profile for user: {current_user.email}")
        print(f"Profile data: {profile_data.dict()}")
        
        # Update fields if provided
        if profile_data.first_name is not None:
            current_user.first_name = profile_data.first_name
        if profile_data.last_name is not None:
            current_user.last_name = profile_data.last_name
        if profile_data.date_of_birth is not None:
            try:
                # Handle different date formats
                date_str = profile_data.date_of_birth.replace('Z', '+00:00')
                current_user.date_of_birth = datetime.fromisoformat(date_str)
            except Exception as date_error:
                print(f"Date parsing error: {date_error}")
                # Try alternative parsing
                current_user.date_of_birth = datetime.strptime(profile_data.date_of_birth.split('T')[0], '%Y-%m-%d')
        if profile_data.phone_number is not None:
            current_user.phone_number = profile_data.phone_number
        if profile_data.address_street is not None:
            current_user.address_street = profile_data.address_street
        if profile_data.address_city is not None:
            current_user.address_city = profile_data.address_city
        if profile_data.address_state is not None:
            current_user.address_state = profile_data.address_state
        if profile_data.address_zip is not None:
            current_user.address_zip = profile_data.address_zip
        if profile_data.address_country is not None:
            current_user.address_country = profile_data.address_country
        if profile_data.emergency_contact_name is not None:
            current_user.emergency_contact_name = profile_data.emergency_contact_name
        if profile_data.emergency_contact_phone is not None:
            current_user.emergency_contact_phone = profile_data.emergency_contact_phone
        if profile_data.emergency_contact_relationship is not None:
            current_user.emergency_contact_relationship = profile_data.emergency_contact_relationship
        
        db.commit()
        db.refresh(current_user)
        
        print(f"✅ Profile updated successfully for {current_user.email}")
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating profile: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/")
async def get_patients(db: Session = Depends(get_db)):
    """Get all patients - placeholder endpoint"""
    return {"message": "Patients endpoint - implementation needed"}


@router.get("/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get specific patient - placeholder endpoint"""
    return {"message": f"Patient {patient_id} endpoint - implementation needed"}