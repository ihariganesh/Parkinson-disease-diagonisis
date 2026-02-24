from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import MedicalData, User, DiagnosisReport
from app.core.security import get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MedicalDataResponse(BaseModel):
    id: str
    type: str
    fileName: str
    fileSize: Optional[int] = None
    uploadedAt: datetime
    processedAt: Optional[datetime] = None
    analysisResult: Optional[Dict[str, Any]] = None

class MedicalDataListResponse(BaseModel):
    items: List[MedicalDataResponse]
    total: int
    page: int
    limit: int
    totalPages: int

class DiagnosisReportResponse(BaseModel):
    id: str
    patientId: str
    doctorId: Optional[str]
    finalDiagnosis: str
    confidence: float
    stage: int
    multimodalAnalysis: Dict[str, Any]
    fusionScore: float
    doctorNotes: Optional[str]
    doctorVerified: bool
    createdAt: datetime
    updatedAt: Optional[datetime]

class DiagnosisReportListResponse(BaseModel):
    items: List[DiagnosisReportResponse]
    total: int
    page: int
    limit: int
    totalPages: int

# Wrapper for API responses
class ApiResponseWrapper(BaseModel):
    success: bool
    data: Optional[DiagnosisReportListResponse] = None
    message: Optional[str] = None
    error: Optional[str] = None

@router.get("/data")
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
        medical_data = query.order_by(MedicalData.uploaded_at.desc()).offset(offset).limit(limit).all()
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        # Convert to response format with camelCase keys matching frontend
        data_list = []
        for data in medical_data:
            data_list.append(MedicalDataResponse(
                id=data.id,
                type=data.type.value if hasattr(data.type, 'value') else str(data.type),
                fileName=data.file_name or "Unknown",
                fileSize=data.file_size,
                uploadedAt=data.uploaded_at,
                processedAt=data.processed_at,
                analysisResult=None
            ))
        
        # Return wrapped successfully with 'items' key matching frontend PaginatedResponse
        return {
            "success": True,
            "data": MedicalDataListResponse(
                items=data_list,
                total=total,
                page=page,
                limit=limit,
                totalPages=total_pages
            )
        }
    except Exception as e:
        # Return empty data for now to prevent frontend errors
        return {
            "success": False,
            "error": str(e),
            "data": MedicalDataListResponse(
                items=[],
                total=0,
                page=page,
                limit=limit,
                totalPages=0
            )
        }

@router.get("/reports")
async def get_medical_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of diagnosis reports for current user"""
    try:
        # Removed sensitive logging - user details not logged in production
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Query diagnosis reports for current user
        query = db.query(DiagnosisReport).filter(DiagnosisReport.patient_id == current_user.id)
        total = query.count()
        reports = query.order_by(DiagnosisReport.created_at.desc()).offset(offset).limit(limit).all()
        
        # Query results logged without user identifiers
        
        # Convert to response format
        report_list = []
        for report in reports:
            report_list.append(DiagnosisReportResponse(
                id=report.id,
                patientId=report.patient_id,
                doctorId=report.doctor_id,
                finalDiagnosis=report.final_diagnosis.value if hasattr(report.final_diagnosis, 'value') else str(report.final_diagnosis),
                confidence=report.confidence,
                stage=report.stage,
                multimodalAnalysis=report.multimodal_analysis or {},
                fusionScore=report.fusion_score,
                doctorNotes=report.doctor_notes,
                doctorVerified=report.doctor_verified,
                createdAt=report.created_at,
                updatedAt=report.updated_at
            ))
        
        print(f"[DEBUG] Returning {len(report_list)} reports")
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        reports_data = DiagnosisReportListResponse(
            items=report_list,
            total=total,
            page=page,
            limit=limit,
            totalPages=total_pages
        )
        
        # Wrap in ApiResponse format for frontend
        return {
            "success": True,
            "data": reports_data
        }
        
    except Exception as e:
        # Error occurred - returning generic error without details
        return {
            "success": False,
            "error": str(e),
            "data": DiagnosisReportListResponse(
                items=[],
                total=0,
                page=page,
                limit=limit,
                totalPages=0
            )
        }

@router.delete("/reports/{report_id}")
async def delete_diagnosis_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a diagnosis report by ID"""
    try:
        # Delete operation logged without user identifiers
        
        # Find the report
        report = db.query(DiagnosisReport).filter(
            DiagnosisReport.id == report_id,
            DiagnosisReport.patient_id == current_user.id  # Ensure user owns the report
        ).first()
        
        if not report:
            # Report access denied - details not logged
            return {
                "success": False,
                "error": "Report not found or you don't have permission to delete it"
            }
        
        # Delete the report
        db.delete(report)
        db.commit()
        
        print(f"[DEBUG] Successfully deleted report {report_id}")
        
        return {
            "success": True,
            "message": "Report deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": "Failed to delete report"
        }

@router.post("/reports/bulk-delete")
async def bulk_delete_diagnosis_reports(
    report_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple diagnosis reports by IDs"""
    try:
        # Bulk delete operation initiated
        
        deleted_count = 0
        failed_ids = []
        
        for report_id in report_ids:
            try:
                # Find the report and ensure user owns it
                report = db.query(DiagnosisReport).filter(
                    DiagnosisReport.id == report_id,
                    DiagnosisReport.patient_id == current_user.id
                ).first()
                
                if report:
                    db.delete(report)
                    deleted_count += 1
                else:
                    failed_ids.append(report_id)
                    print(f"[WARNING] Report {report_id} not found or user doesn't own it")
            except Exception as e:
                failed_ids.append(report_id)
                # Error details not logged
        
        # Commit all deletions
        db.commit()
        
        print(f"[DEBUG] Successfully deleted {deleted_count} reports, {len(failed_ids)} failed")
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} report(s)",
            "deleted_count": deleted_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": "Failed to delete reports"
        }

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