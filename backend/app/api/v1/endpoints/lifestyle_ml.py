"""
Lifestyle Recommendation ML API Endpoint
1. ML model predicts recommendations from user profile + Parkinson's diagnosis
2. Llama 3.2 (via Ollama) validates and refines the recommendations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.ml.lifestyle_predictor import get_lifestyle_predictor
from app.services.ollama_service import validate_and_refine_recommendations, check_ollama_health

router = APIRouter()


class LifestylePredictionRequest(BaseModel):
    gender: str = Field(..., description="Gender: 'Male' or 'Female'")
    age: int = Field(..., ge=18, le=120, description="Age in years")
    address: str = Field(..., description="Location/address (e.g., 'Chennai TN India')")
    previous_condition: str = Field(
        ...,
        description="Health condition: 'None', 'Diabetes', 'Hypertension', etc."
    )
    parkinson_status: int = Field(0, ge=0, le=1, description="0=No PD, 1=Has PD")
    parkinson_stage: int = Field(0, ge=0, le=3, description="0=Healthy, 1=Early, 2=Moderate, 3=Advanced")


class RecommendationDetail(BaseModel):
    category: str
    recommendation: str
    details: List[str]
    priority: str
    ai_note: Optional[str] = None


class LifestylePredictionResponse(BaseModel):
    success: bool
    source: str
    llama_validated: bool
    llama_available: bool
    corrections_made: bool
    general_advice: Optional[str] = None
    input: Dict[str, Any]
    recommendations: Dict[str, RecommendationDetail]
    model_accuracy: float


@router.post("/predict", response_model=LifestylePredictionResponse)
async def predict_lifestyle(request: LifestylePredictionRequest):
    """
    1. ML model predicts lifestyle recommendations
    2. Llama 3.2 validates and refines them for medical accuracy
    """
    predictor = get_lifestyle_predictor()

    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Lifestyle model not loaded. Please train the model first."
        )

    # Step 1: ML Prediction
    ml_result = predictor.predict(
        gender=request.gender,
        age=request.age,
        address=request.address,
        previous_condition=request.previous_condition,
        parkinson_status=request.parkinson_status,
        parkinson_stage=request.parkinson_stage,
    )

    ml_recs = ml_result.get("recommendations", {})
    ml_input = ml_result.get("input", {})

    # Step 2: Llama 3.2 Validation
    user_profile = {
        "gender": ml_input.get("gender", request.gender),
        "age": ml_input.get("age", request.age),
        "location": ml_input.get("location", request.address),
        "previous_condition": ml_input.get("previous_condition", request.previous_condition),
        "parkinson_status": ml_input.get("parkinson_status", request.parkinson_status),
        "parkinson_stage": ml_input.get("parkinson_stage", request.parkinson_stage),
    }

    llama_result = await validate_and_refine_recommendations(
        user_profile=user_profile,
        ml_recommendations=ml_recs,
    )

    llama_validated = llama_result.get("validated", False)
    llama_available = llama_result.get("llama_available", False)
    corrections_made = llama_result.get("corrections_made", False)
    general_advice = llama_result.get("general_advice", None)
    refined_recs = llama_result.get("recommendations", ml_recs)

    return LifestylePredictionResponse(
        success=True,
        source="ml_model + llama_validation" if llama_validated else "ml_model",
        llama_validated=llama_validated,
        llama_available=llama_available,
        corrections_made=corrections_made,
        general_advice=general_advice,
        input=ml_input,
        recommendations=refined_recs,
        model_accuracy=ml_result.get("model_accuracy", 0),
    )


@router.get("/conditions")
async def get_available_conditions():
    predictor = get_lifestyle_predictor()
    conditions = predictor.get_available_conditions()
    return {
        "success": True,
        "conditions": conditions,
        "parkinson_stages": {
            0: "No Parkinson (healthy)",
            1: "Early Stage (mild symptoms)",
            2: "Moderate Stage",
            3: "Advanced Stage",
        },
    }


@router.get("/model-info")
async def get_model_info():
    predictor = get_lifestyle_predictor()
    ollama_ok = await check_ollama_health()
    if not predictor.is_ready():
        return {"success": False, "message": "Model not loaded"}
    return {
        "success": True,
        "metadata": predictor.metadata,
        "llama_available": ollama_ok,
    }
