from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserRole
from app.core.security import verify_password, create_access_token, get_password_hash, decode_access_token
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "PATIENT"  # PATIENT or DOCTOR
    date_of_birth: str = None
    phone_number: str = None
    gender: str = None  # male, female, other, prefer_not_to_say
    # Address fields
    address_street: str = None
    address_city: str = None
    address_state: str = None
    address_zip: str = None
    address_country: str = None
    # Emergency contact fields
    emergency_contact_name: str = None
    emergency_contact_phone: str = None
    emergency_contact_relationship: str = None
    # Doctor-specific fields
    license_number: str = None
    specialization: str = None
    hospital: str = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    patient_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

def generate_patient_id(db: Session) -> str:
    """Generate a unique patient ID in format PID-XXXXXX"""
    while True:
        # Get the count of existing patient IDs to generate next number
        count = db.query(User).filter(User.patient_id.isnot(None)).count()
        new_number = count + 1
        patient_id = f"PID-{new_number:06d}"  # PID-000001, PID-000002, etc.
        
        # Check if this ID already exists (in case of concurrent registrations)
        existing = db.query(User).filter(User.patient_id == patient_id).first()
        if not existing:
            return patient_id

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())
    
    # Convert role string to enum
    role_enum = UserRole.PATIENT if user_data.role.upper() == "PATIENT" else UserRole.DOCTOR
    
    # Generate patient ID for patients only
    patient_id = generate_patient_id(db) if role_enum == UserRole.PATIENT else None
    
    # Parse date_of_birth if provided
    date_of_birth = None
    if user_data.date_of_birth:
        try:
            date_of_birth = datetime.strptime(user_data.date_of_birth, "%Y-%m-%d")
        except ValueError:
            pass
    
    db_user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=role_enum,
        patient_id=patient_id,
        date_of_birth=date_of_birth,
        phone_number=user_data.phone_number,
        gender=user_data.gender,
        # Address fields
        address_street=user_data.address_street,
        address_city=user_data.address_city,
        address_state=user_data.address_state,
        address_zip=user_data.address_zip,
        address_country=user_data.address_country,
        # Emergency contact fields
        emergency_contact_name=user_data.emergency_contact_name,
        emergency_contact_phone=user_data.emergency_contact_phone,
        emergency_contact_relationship=user_data.emergency_contact_relationship,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    response_data = {
        "message": "User registered successfully",
        "user_id": db_user.id,
        "email": db_user.email
    }
    
    if db_user.patient_id:
        response_data["patient_id"] = db_user.patient_id
    
    return response_data

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        is_active=user.is_active,
        created_at=user.created_at
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        patient_id=current_user.patient_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        date_of_birth=current_user.date_of_birth,
        phone_number=current_user.phone_number,
        gender=current_user.gender,
        address_street=current_user.address_street,
        address_city=current_user.address_city,
        address_state=current_user.address_state,
        address_zip=current_user.address_zip,
        address_country=current_user.address_country
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user - for stateless JWT, this is mainly for frontend token cleanup"""
    return {"message": "Successfully logged out", "user_id": current_user.id}