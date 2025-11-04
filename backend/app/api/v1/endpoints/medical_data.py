from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import MedicalData, User
from app.core.security import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MedicalDataResponse(BaseModel):
    id: str
    data_type: str
    file_name: str
    file_size: Optional[int]
    uploaded_at: datetime
    processed_at: Optional[datetime]

class MedicalDataListResponse(BaseModel):
    data: List[MedicalDataResponse]
    total: int
    page: int
    limit: int

@router.get("/data", response_model=MedicalDataListResponse)
async def get_medical_data_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of medical data for current user"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Query medical data for current user
        query = db.query(MedicalData).filter(MedicalData.patient_id == current_user.id)
        total = query.count()
        medical_data = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        data_list = []
        for data in medical_data:
            data_list.append(MedicalDataResponse(
                id=data.id,
                data_type=data.type.value if hasattr(data.type, 'value') else str(data.type),
                file_name=data.file_name or "Unknown",
                file_size=data.file_size,
                uploaded_at=data.uploaded_at,
                processed_at=data.processed_at
            ))
        
        return MedicalDataListResponse(
            data=data_list,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        # Return empty data for now to prevent frontend errors
        return MedicalDataListResponse(
            data=[],
            total=0,
            page=page,
            limit=limit
        )

@router.get("/reports", response_model=MedicalDataListResponse)
async def get_medical_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of medical reports for current user"""
    try:
        # For now, return empty list as reports are not yet implemented
        return MedicalDataListResponse(
            data=[],
            total=0,
            page=page,
            limit=limit
        )
    except Exception as e:
        return MedicalDataListResponse(
            data=[],
            total=0,
            page=page,
            limit=limit
        )

@router.post("/upload")
async def upload_medical_data(
    file: UploadFile = File(...),
    data_type: str = "mri",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload medical data file"""
    return {"message": f"Medical data upload endpoint - file: {file.filename}, type: {data_type}"}

@router.get("/{data_id}")
async def get_medical_data(
    data_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific medical data"""
    return {"message": f"Medical data {data_id} endpoint - implementation needed"}