from fastapi import APIRouter
from app.api.v1.endpoints import auth, patients, doctors, medical_data, analysis, handwriting, doctor, invitation, messages, chatbot, lifestyle_ml
from app.api.v1 import lifestyle

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(doctor.router, tags=["doctor"])  # Doctor dashboard routes
api_router.include_router(invitation.router, tags=["invitation"])  # Doctor-patient linking
api_router.include_router(medical_data.router, prefix="/medical", tags=["medical"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(handwriting.router, prefix="/handwriting", tags=["handwriting"])
api_router.include_router(lifestyle.router, tags=["lifestyle"])
api_router.include_router(lifestyle_ml.router, prefix="/lifestyle-ml", tags=["lifestyle-ml"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Parkinson's Detection API is running"}