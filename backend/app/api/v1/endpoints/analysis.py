from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.db.models import User
import os
import sys
from typing import Optional
import logging

# Add the ml-models directory to the Python path
ml_models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../ml-models"))
if ml_models_path not in sys.path:
    sys.path.insert(0, ml_models_path)

try:
    # Try to import both original and enhanced speech analysis services
    import importlib.util
    
    # Try to import the enhanced service first
    speech_service_v2_path = os.path.join(ml_models_path, "speech_analysis_service_v2.py")
    speech_service_path = os.path.join(ml_models_path, "speech_analysis_service.py")
    
    # Preference for V2 service if available
    if os.path.exists(speech_service_v2_path):
        spec = importlib.util.spec_from_file_location("speech_analysis_service_v2", speech_service_v2_path)
        speech_analysis_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(speech_analysis_module)
        
        analyze_speech_bytes = speech_analysis_module.analyze_speech_bytes_v2
        SpeechAnalysisService = speech_analysis_module.SpeechAnalysisServiceV2
        
        # Initialize with correct models path
        speech_service = SpeechAnalysisService(models_dir=os.path.join(ml_models_path, "models/speech"))
        SPEECH_ANALYSIS_AVAILABLE = True
        SPEECH_SERVICE_VERSION = "v2"
        logging.info("✓ Using enhanced speech analysis service v2")
        
    elif os.path.exists(speech_service_path):
        spec = importlib.util.spec_from_file_location("speech_analysis_service", speech_service_path)
        speech_analysis_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(speech_analysis_module)
        
        analyze_speech_bytes = speech_analysis_module.analyze_speech_bytes
        SpeechAnalysisService = speech_analysis_module.SpeechAnalysisService
        
        # Initialize with correct models path
        speech_service = SpeechAnalysisService(models_dir=os.path.join(ml_models_path, "models/speech"))
        SPEECH_ANALYSIS_AVAILABLE = True
        SPEECH_SERVICE_VERSION = "v1"
        logging.info("✓ Using original speech analysis service v1")
    else:
        raise ImportError(f"No speech analysis service found. Checked paths: {[speech_service_v2_path, speech_service_path]}")
        
except (ImportError, AttributeError, Exception) as e:
    logging.warning(f"Speech analysis not available: {e}")
    logging.warning(f"ML models path: {ml_models_path}")
    logging.warning(f"Python path includes: {sys.path}")
    logging.warning("Check that speech analysis service files exist in the ml-models directory.")
    SPEECH_ANALYSIS_AVAILABLE = False
    SPEECH_SERVICE_VERSION = None
    speech_service = None
    analyze_speech_bytes = None
    SpeechAnalysisService = None

# Speech analysis and handwriting analysis only - MRI analysis removed
# MRI components removed to clean up space

# ========================= DAT SCAN ANALYSIS SERVICE INITIALIZATION =========================
dat_service = None
DAT_ANALYSIS_AVAILABLE = False

try:
    from app.services.dat_service_direct import get_dat_analysis_service
    dat_service = get_dat_analysis_service()
    DAT_ANALYSIS_AVAILABLE = dat_service.is_available()
    if DAT_ANALYSIS_AVAILABLE:
        logging.info("✓ DaT scan analysis service loaded successfully")
    else:
        logging.warning("DaT scan analysis service initialized but model not loaded")
except Exception as e:
    logging.warning(f"DaT scan analysis not available: {e}")
    import traceback
    logging.warning(traceback.format_exc())
    DAT_ANALYSIS_AVAILABLE = False
    dat_service = None

# ========================= MRI ANALYSIS SERVICE INITIALIZATION =========================
mri_service = None
MRI_ANALYSIS_AVAILABLE = False

try:
    import importlib.util
    mri_models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../ml-models"))
    mri_service_path = os.path.join(mri_models_path, "mri_analysis_service.py")
    if os.path.exists(mri_service_path):
        spec = importlib.util.spec_from_file_location("mri_analysis_service", mri_service_path)
        mri_analysis_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mri_analysis_module)
        MRIAnalysisService = getattr(mri_analysis_module, "MRIAnalysisService", None)
        if MRIAnalysisService:
            mri_service = MRIAnalysisService(models_dir=os.path.join(mri_models_path, "models/mri"))
            MRI_ANALYSIS_AVAILABLE = True
            logging.info("✓ MRI analysis service loaded successfully")
        else:
            logging.warning("MRIAnalysisService class not found in mri_analysis_service.py")
    else:
        logging.warning(f"MRI analysis service file not found at {mri_service_path}")
except Exception as e:
    logging.warning(f"MRI analysis not available: {e}")
    MRI_ANALYSIS_AVAILABLE = False
    mri_service = None

router = APIRouter()

def init_speech_service():
    """Initialize speech service if not already initialized"""
    global speech_service
    if speech_service is None and SPEECH_ANALYSIS_AVAILABLE:
        try:
            # Try to initialize the service
            if SpeechAnalysisService:
                speech_service = SpeechAnalysisService(models_dir=os.path.join(ml_models_path, "models/speech"))
                logging.info(f"✓ Initialized speech service {SPEECH_SERVICE_VERSION}")
        except Exception as e:
            logging.error(f"Failed to initialize speech service: {e}")

@router.post("/analyze")
async def analyze_medical_data(
    data_id: int,
    analysis_type: str = "parkinson_detection",
    db: Session = Depends(get_db)
):
    """Analyze medical data - placeholder endpoint"""
    return {"message": f"Analysis endpoint - data_id: {data_id}, type: {analysis_type}"}

@router.get("/results/{result_id}")
async def get_analysis_result(result_id: int, db: Session = Depends(get_db)):
    """Get analysis result - placeholder endpoint"""
    return {"message": f"Analysis result {result_id} endpoint - implementation needed"}

@router.post("/speech/analyze")
async def analyze_speech(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze speech recording for Parkinson's disease detection"""
    
    if not SPEECH_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Speech analysis service is not available. Please ensure all dependencies are installed."
        )
    
    # Validate file type
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload an audio file (WAV, MP3, M4A, FLAC, or OGG)."
        )
    
    # Validate file size (limit to 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Please upload a file smaller than 50MB."
        )
    
    try:
        # Read file contents
        audio_bytes = await file.read()
        
        # Check if service is available
        if speech_service is None:
            raise HTTPException(
                status_code=503,
                detail="Speech analysis service is not available."
            )
        
        # Analyze the speech using the initialized service
        result = speech_service.analyze_audio_from_bytes(audio_bytes, file.filename)
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Speech analysis failed. Please try again with a different audio file."
            )
        
        # Add user and file information to the result
        result.update({
            "user_id": current_user.id,
            "filename": file.filename,
            "file_size": len(audio_bytes),
            "analysis_type": "speech_parkinson_detection"
        })
        
        return {
            "success": True,
            "message": "Speech analysis completed successfully",
            "analysis_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Speech analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during speech analysis: {str(e)}"
        )

@router.get("/speech/health")
async def speech_analysis_health():
    """Check if speech analysis service is available with detailed information"""
    if not SPEECH_ANALYSIS_AVAILABLE:
        return {
            "available": False,
            "version": None,
            "message": "Speech analysis service is not available",
            "dependencies_required": [
                "tensorflow",
                "librosa", 
                "praat-parselmouth",
                "numpy",
                "pandas",
                "scikit-learn",
                "soundfile"
            ],
            "recommendations": [
                "Install required dependencies",
                "Ensure model files are available",
                "Check ml-models directory structure"
            ]
        }
    
    try:
        if speech_service is None:
            return {
                "available": True,
                "version": SPEECH_SERVICE_VERSION,
                "model_loaded": False,
                "message": "Speech service not initialized"
            }
        
        # Check if it's the enhanced service with system info
        if hasattr(speech_service, 'get_system_info'):
            # Enhanced service v2
            system_info = speech_service.get_system_info()
            model_loaded = system_info['model_loaded']
            
            return {
                "available": True,
                "version": SPEECH_SERVICE_VERSION,
                "service_version": system_info.get('service_version', '2.0'),
                "model_loaded": model_loaded,
                "feature_extractor": system_info['feature_extractor'],
                "compatibility": system_info.get('compatibility'),
                "recommendations": system_info.get('recommendations', []),
                "message": "Enhanced speech analysis service is available" if model_loaded else "Service available but model not loaded"
            }
        else:
            # Original service v1
            try:
                model_loaded = speech_service.is_loaded or speech_service.load_models()
            except:
                model_loaded = False
            
            return {
                "available": True,
                "version": SPEECH_SERVICE_VERSION,
                "service_version": "1.0",
                "model_loaded": model_loaded,
                "message": "Speech analysis service is available" if model_loaded else "Service available but model not loaded",
                "recommendations": [
                    "Consider upgrading to enhanced service v2 for better feature validation",
                    "Install praat-parselmouth for improved feature extraction"
                ]
            }
            
    except Exception as e:
        return {
            "available": True,
            "version": SPEECH_SERVICE_VERSION,
            "model_loaded": False,
            "error": str(e),
            "message": f"Service available but error during health check: {str(e)}"
        }

@router.post("/speech/demo-analyze")
async def demo_analyze_speech(
    file: UploadFile = File(...)
):
    """Public demo endpoint for speech analysis without authentication"""
    
    if not SPEECH_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Speech analysis service is not available. Please ensure all dependencies are installed."
        )
    
    # Debug logging for demo endpoint
    print(f"🔍 Demo endpoint - Received file: '{file.filename}'")
    print(f"🔍 Demo endpoint - File content type: '{file.content_type}'")
    print(f"🔍 Demo endpoint - Filename ends with mp3? {file.filename.lower().endswith('.mp3') if file.filename else 'No filename'}")
    
    # Validate file type
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
        print(f"❌ Demo endpoint - File validation failed for: '{file.filename}'")
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload an audio file (WAV, MP3, M4A, FLAC, or OGG)."
        )
    
    # Validate file size (limit to 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Please upload a file smaller than 50MB."
        )
    
    try:
        # Read file contents
        audio_bytes = await file.read()
        
        # Check if service is available
        if speech_service is None:
            raise HTTPException(
                status_code=503,
                detail="Speech analysis service is not available."
            )
        
        # Analyze the speech using the initialized service
        result = speech_service.analyze_audio_from_bytes(audio_bytes, file.filename)
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Speech analysis failed. Please try again with a different audio file."
            )
        
        # Add demo information to the result (no user ID for public demo)
        demo_info = {
            "filename": file.filename,
            "file_size": len(audio_bytes),
            "analysis_type": "speech_parkinson_detection_demo",
            "demo_mode": True
        }
        
        # Enhanced information if using enhanced service
        if hasattr(speech_service, 'get_system_info'):
            system_info = speech_service.get_system_info()
            demo_info.update({
                "service_version": system_info.get('service_version', '2.0'),
                "feature_extraction": system_info['feature_extractor'],
                "compatibility_score": system_info.get('compatibility', {}).get('score', 'unknown'),
                "features_extracted": result.get('features_count', 'unknown')
            })
        else:
            demo_info.update({
                "service_version": "1.0",
                "note": "Using original service - consider upgrading to v2 for enhanced features"
            })
        
        result.update(demo_info)
        
        return {
            "success": True,
            "message": "Speech analysis completed successfully",
            "analysis_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Demo speech analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during speech analysis: {str(e)}"
        )

@router.post("/speech/test-analyze")
async def test_speech_analysis():
    """Simple demo endpoint that uses the test audio file for analysis"""
    if not SPEECH_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Speech analysis service is not available. Please check dependencies."
        )
    
    try:
        # Try to load service if not already loaded
        if speech_service is None:
            # Initialize the service (this will load the appropriate version)
            pass  # Service is already initialized globally
            
        if speech_service is None:
            raise HTTPException(
                status_code=503,
                detail="Failed to initialize speech analysis service"
            )
        
        # Use test audio file from project root
        test_audio_path = "/home/hari/Downloads/parkinson/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            # Try mp3 format
            test_audio_path = "/home/hari/Downloads/parkinson/test_audio.mp3"
            if not os.path.exists(test_audio_path):
                raise HTTPException(
                    status_code=404,
                    detail="Test audio file not found. Expected test_audio.wav or test_audio.mp3 in project root."
                )
        
        # Perform analysis
        result = speech_service.analyze_audio(test_audio_path)
        
        # Enhanced result with system information if using enhanced service
        if hasattr(speech_service, 'get_system_info'):
            system_info = speech_service.get_system_info()
            result.update({
                "test_demo_info": {
                    "test_file": os.path.basename(test_audio_path),
                    "service_version": system_info.get('service_version', '2.0'),
                    "feature_extraction": system_info['feature_extractor'],
                    "compatibility_score": system_info.get('compatibility', {}).get('score', 'unknown'),
                    "features_extracted": result.get('features_count', 'unknown')
                }
            })
        else:
            result.update({
                "test_demo_info": {
                    "test_file": os.path.basename(test_audio_path),
                    "service_version": "1.0",
                    "note": "Using original service - consider upgrading to v2 for enhanced features"
                }
            })
        
        return {
            "success": True,
            "message": "Test audio analysis completed successfully",
            "analysis_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Test demo analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Test demo analysis failed: {str(e)}"
        )

@router.post("/speech/batch-analyze")
async def batch_analyze_speech(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze multiple speech recordings for Parkinson's disease detection"""
    
    if not SPEECH_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Speech analysis service is not available."
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum 10 files allowed per batch."
        )
    
    results = []
    errors = []
    
    for file in files:
        try:
            # Validate file
            if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
                errors.append({
                    "filename": file.filename,
                    "error": "Invalid file format"
                })
                continue
                
            # Read and analyze
            audio_bytes = await file.read()
            
            # Check if service is available
            if speech_service is None:
                errors.append({
                    "filename": file.filename,
                    "error": "Speech analysis service not available"
                })
                continue
                
            result = speech_service.analyze_audio_from_bytes(audio_bytes, file.filename)
            
            if result:
                result.update({
                    "user_id": current_user.id,
                    "filename": file.filename,
                    "file_size": len(audio_bytes)
                })
                results.append(result)
            else:
                errors.append({
                    "filename": file.filename,
                    "error": "Analysis failed"
                })
                
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": True,
        "processed_files": len(results),
        "failed_files": len(errors),
        "results": results,
        "errors": errors
    }

# ========================= DAT SCAN ANALYSIS ENDPOINTS =========================

@router.post("/dat/analyze")
async def analyze_dat_scan(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze DaT scan (multiple slices) for Parkinson's disease detection
    Accepts multiple image files representing scan slices
    """
    
    if not DAT_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="DaT scan analysis service is not available. Model may not be trained yet."
        )
    
    # Validate we have at least one file
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded. Please upload DaT scan slices."
        )
    
    # Validate file types
    valid_extensions = ('.png', '.jpg', '.jpeg', '.dcm')
    for file in files:
        if not file.filename.lower().endswith(valid_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format for {file.filename}. Please upload image files (PNG, JPG, JPEG, or DICOM)."
            )
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../uploads/dat_scans"))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded files temporarily
        import uuid
        from datetime import datetime
        
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(upload_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        file_paths = []
        for file in files:
            # Save file
            file_path = os.path.join(session_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            file_paths.append(file_path)
        
        # Analyze scan using directory
        result = dat_service.predict(session_dir)
        
        # Clean up uploaded files (optional, you may want to keep them)
        # import shutil
        # shutil.rmtree(session_dir)
        
        if result.get('success'):
            return {
                "success": True,
                "message": "DaT scan analyzed successfully",
                "user_id": current_user.id,
                "num_slices": len(files),
                "session_id": session_id,
                **result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Analysis failed')
            )
    
    except Exception as e:
        logging.error(f"DaT scan analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during DaT scan analysis: {str(e)}"
        )

@router.get("/dat/status")
async def get_dat_service_status():
    """Get DaT scan analysis service status"""
    if dat_service:
        return dat_service.get_status()
    else:
        return {
            "service_name": "DaT Scan Analysis",
            "available": False,
            "error": "Service not initialized"
        }


# ========================= MULTI-MODAL ANALYSIS =========================

from typing import List
from fastapi import Form
from pathlib import Path
import tempfile
import shutil

# Initialize multi-modal service
try:
    from app.services.multimodal_service import get_multimodal_service
    multimodal_service = get_multimodal_service()
    MULTIMODAL_AVAILABLE = True
    logging.info("✓ Multi-modal analysis service initialized")
except Exception as e:
    MULTIMODAL_AVAILABLE = False
    multimodal_service = None
    logging.error(f"✗ Multi-modal analysis service not available: {e}")


@router.post("/multimodal/comprehensive")
async def analyze_comprehensive(
    dat_scans: Optional[List[UploadFile]] = File(None),
    handwriting_spiral: Optional[UploadFile] = File(None),
    handwriting_wave: Optional[UploadFile] = File(None),
    voice_recording: Optional[UploadFile] = File(None),
    patient_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive multi-modal Parkinson's disease analysis
    Combines DaT scan, handwriting, and voice analysis
    
    Args:
        dat_scans: List of DaT scan images (12-16 images)
        handwriting_spiral: Spiral drawing image
        handwriting_wave: Wave drawing image
        voice_recording: Voice audio file
        patient_id: Optional patient identifier
    
    Returns:
        Comprehensive analysis with multi-modal fusion
    """
    
    if not MULTIMODAL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Multi-modal analysis service is not available"
        )
    
    # Validate at least one modality is provided
    if not any([dat_scans, handwriting_spiral, handwriting_wave, voice_recording]):
        raise HTTPException(
            status_code=400,
            detail="At least one modality (DaT scan, handwriting, or voice) must be provided"
        )
    
    try:
        # Create temporary directories for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Process DaT scans
            dat_scan_paths = None
            if dat_scans:
                dat_dir = temp_path / "dat_scans"
                dat_dir.mkdir()
                dat_scan_paths = []
                
                for i, scan_file in enumerate(dat_scans):
                    scan_path = dat_dir / f"scan_{i:03d}.png"
                    with open(scan_path, "wb") as f:
                        content = await scan_file.read()
                        f.write(content)
                    dat_scan_paths.append(scan_path)
            
            # Process handwriting images
            spiral_path = None
            if handwriting_spiral:
                spiral_path = temp_path / "spiral.png"
                with open(spiral_path, "wb") as f:
                    content = await handwriting_spiral.read()
                    f.write(content)
            
            wave_path = None
            if handwriting_wave:
                wave_path = temp_path / "wave.png"
                with open(wave_path, "wb") as f:
                    content = await handwriting_wave.read()
                    f.write(content)
            
            # Process voice recording
            voice_path = None
            if voice_recording:
                # Get file extension
                filename = voice_recording.filename or "recording.wav"
                ext = filename.split('.')[-1]
                voice_path = temp_path / f"voice.{ext}"
                with open(voice_path, "wb") as f:
                    content = await voice_recording.read()
                    f.write(content)
            
            # Perform multi-modal analysis
            result = multimodal_service.analyze_comprehensive(
                dat_scans=dat_scan_paths,
                handwriting_spiral=spiral_path,
                handwriting_wave=wave_path,
                voice_file=voice_path,
                patient_id=patient_id
            )
            
            # Save diagnosis report to database
            try:
                import uuid
                from app.db.models import DiagnosisReport, DiagnosisStage
                
                # Map fusion diagnosis to DiagnosisStage enum
                diagnosis_mapping = {
                    'healthy': DiagnosisStage.HEALTHY,
                    'parkinson': DiagnosisStage.EARLY_STAGE,
                    'early_stage': DiagnosisStage.EARLY_STAGE,
                    'moderate_stage': DiagnosisStage.MODERATE_STAGE,
                    'advanced_stage': DiagnosisStage.ADVANCED_STAGE
                }
                
                fusion_results = result.get('fusion_results', {})
                final_diagnosis = fusion_results.get('final_diagnosis', 'healthy').lower()
                confidence = fusion_results.get('final_probability', 0.0)
                
                # Determine stage (0-4 scale)
                stage = 0
                if final_diagnosis == 'healthy':
                    stage = 0
                    diagnosis_stage = DiagnosisStage.HEALTHY
                elif final_diagnosis in ['parkinson', 'early_stage']:
                    stage = 1
                    diagnosis_stage = DiagnosisStage.EARLY_STAGE
                elif final_diagnosis == 'moderate_stage':
                    stage = 2
                    diagnosis_stage = DiagnosisStage.MODERATE_STAGE
                elif final_diagnosis == 'advanced_stage':
                    stage = 3
                    diagnosis_stage = DiagnosisStage.ADVANCED_STAGE
                else:
                    stage = 0
                    diagnosis_stage = DiagnosisStage.HEALTHY
                
                # Prepare multimodal analysis data
                multimodal_analysis = {
                    'dat_scan': result.get('modality_results', {}).get('dat'),
                    'handwriting': result.get('modality_results', {}).get('handwriting'),
                    'voice': result.get('modality_results', {}).get('voice'),
                    'fusion_results': fusion_results,
                    'clinical_interpretation': result.get('clinical_interpretation'),
                    'recommendations': result.get('recommendations')
                }
                
                # Create diagnosis report
                diagnosis_report = DiagnosisReport(
                    id=str(uuid.uuid4()),
                    patient_id=current_user.id,  # Use authenticated user ID
                    doctor_id=None,  # No doctor assigned yet
                    final_diagnosis=diagnosis_stage,
                    confidence=confidence,
                    stage=stage,
                    multimodal_analysis=multimodal_analysis,
                    fusion_score=fusion_results.get('agreement_score', 0.0),
                    doctor_notes=None,
                    doctor_verified=False
                )
                
                db.add(diagnosis_report)
                db.commit()
                db.refresh(diagnosis_report)
                
                # Add report ID to result
                result['report_id'] = diagnosis_report.id
                result['saved_to_database'] = True
                
                logging.info(f"✓ Saved diagnosis report {diagnosis_report.id} for user {current_user.id}")
                
            except Exception as save_error:
                logging.error(f"Failed to save diagnosis report: {str(save_error)}")
                result['saved_to_database'] = False
                result['save_error'] = str(save_error)
            
            return result
            
    except Exception as e:
        logging.error(f"Multi-modal analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during multi-modal analysis: {str(e)}"
        )


@router.get("/multimodal/status")
async def get_multimodal_status():
    """Get multi-modal analysis service status"""
    return {
        "service_name": "Multi-Modal Parkinson's Analysis",
        "available": MULTIMODAL_AVAILABLE,
        "modalities": {
            "dat_scan": dat_service is not None,
            "handwriting": True,  # Assumed available
            "voice": SPEECH_ANALYSIS_AVAILABLE
        },
        "weights": {
            "dat": 0.50,
            "handwriting": 0.25,
            "voice": 0.25
        }
    }


# ========================= DEMO ENDPOINTS (NO AUTH REQUIRED) =========================

# MRI analysis endpoints removed to clean up space