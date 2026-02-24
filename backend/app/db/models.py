from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"


class DiagnosisStage(enum.Enum):
    HEALTHY = "healthy"
    EARLY_STAGE = "early_stage"
    MODERATE_STAGE = "moderate_stage"
    ADVANCED_STAGE = "advanced_stage"


class DataType(enum.Enum):
    HANDWRITING = "handwriting"
    VOICE = "voice"
    ECG = "ecg"
    MRI = "mri"
    DOCTOR_NOTES = "doctor_notes"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    patient_id = Column(String, unique=True, index=True, nullable=True)  # Unique patient ID (e.g., PID-001234)
    date_of_birth = Column(DateTime, nullable=True)
    phone_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    
    # Personal information
    gender = Column(String, nullable=True)  # male, female, other, prefer_not_to_say
    
    # Address fields
    address_street = Column(String, nullable=True)
    address_city = Column(String, nullable=True)
    address_state = Column(String, nullable=True)
    address_zip = Column(String, nullable=True)
    address_country = Column(String, nullable=True)
    
    # Emergency contact fields
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_contact_relationship = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    medical_data = relationship("MedicalData", back_populates="patient")
    patient_reports = relationship("DiagnosisReport", foreign_keys="DiagnosisReport.patient_id", back_populates="patient")
    doctor_reports = relationship("DiagnosisReport", foreign_keys="DiagnosisReport.doctor_id", back_populates="doctor")
    
    @property
    def age(self) -> int:
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = datetime.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    medical_record_number = Column(String, unique=True, nullable=False)
    assigned_doctor_id = Column(String, ForeignKey("users.id"), nullable=True)
    emergency_contact = Column(JSON, nullable=True)  # {name, relationship, phone}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigned_doctor = relationship("User", foreign_keys=[assigned_doctor_id])


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    specialization = Column(String, nullable=False)
    hospital = Column(String, nullable=False)
    experience = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class MedicalData(Base):
    __tablename__ = "medical_data"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(DataType), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_metadata = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    patient = relationship("User", back_populates="medical_data")
    analysis_result = relationship("AnalysisResult", back_populates="medical_data", uselist=False)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, index=True)
    medical_data_id = Column(String, ForeignKey("medical_data.id"), nullable=False)
    confidence = Column(Float, nullable=False)
    prediction = Column(Enum(DiagnosisStage), nullable=False)
    stage = Column(Integer, nullable=True)  # 0-4 scale
    features = Column(JSON, nullable=True)  # Extracted features
    model_version = Column(String, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    medical_data = relationship("MedicalData", back_populates="analysis_result")


class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=True)
    final_diagnosis = Column(Enum(DiagnosisStage), nullable=False)
    confidence = Column(Float, nullable=False)
    stage = Column(Integer, nullable=False)  # 0-4 scale
    multimodal_analysis = Column(JSON, nullable=False)  # Analysis results from different modalities
    fusion_score = Column(Float, nullable=False)
    doctor_notes = Column(Text, nullable=True)
    doctor_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_reports")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_reports")
    lifestyle_suggestions = relationship("LifestyleSuggestion", back_populates="report")


class LifestyleSuggestion(Base):
    __tablename__ = "lifestyle_suggestions"

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=False)
    category = Column(String, nullable=False)  # exercise, diet, therapy, medication, lifestyle
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False)  # List of recommendations
    priority = Column(String, nullable=False)  # low, medium, high
    stage = Column(Integer, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    report = relationship("DiagnosisReport", back_populates="lifestyle_suggestions")


class CachedRecommendations(Base):
    __tablename__ = "cached_recommendations"

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=False, unique=True)
    recommendations = Column(JSON, nullable=False)
    generation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    report = relationship("DiagnosisReport")


class HandwritingAnalysis(Base):
    __tablename__ = "handwriting_analyses"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    drawing_type = Column(String, nullable=False)  # 'spiral' or 'wave'
    sentence_prompt = Column(String, nullable=True)  # sentence they were asked to write
    image_path = Column(String, nullable=False)  # path to uploaded image
    prediction = Column(String, nullable=True)  # 'healthy' or 'parkinson'
    confidence_score = Column(Float, nullable=True)  # model confidence (0-1)
    analysis_details = Column(JSON, nullable=True)  # detailed ML analysis results
    model_version = Column(String, nullable=True)  # version of ML model used
    status = Column(String, default="pending")  # pending, analyzing, completed, failed
    error_message = Column(Text, nullable=True)  # if analysis failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class InvitationStatus(enum.Enum):
    """Status of doctor-patient invitation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DoctorInvitation(Base):
    """Doctor invitation codes for patient linking"""
    __tablename__ = "doctor_invitations"

    id = Column(String, primary_key=True, index=True)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    invitation_code = Column(String, unique=True, nullable=False, index=True)
    
    # Invitation details
    max_uses = Column(Integer, default=1)  # How many patients can use this code
    current_uses = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Optional metadata
    description = Column(String, nullable=True)  # "For new patients", "Follow-up patients", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id])
    link_requests = relationship("DoctorPatientLinkRequest", back_populates="invitation")


class DoctorPatientLinkRequest(Base):
    """Patient requests to link with doctor using invitation code"""
    __tablename__ = "doctor_patient_link_requests"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    invitation_id = Column(String, ForeignKey("doctor_invitations.id"), nullable=True)
    
    # Request status
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    patient_message = Column(Text, nullable=True)  # Optional message from patient
    
    # Doctor response
    doctor_response = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    invitation = relationship("DoctorInvitation", back_populates="link_requests")


class DoctorPatientAssignment(Base):
    """Links doctors to their assigned patients (after approval)"""
    __tablename__ = "doctor_patient_assignments"

    id = Column(String, primary_key=True, index=True)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    link_request_id = Column(String, ForeignKey("doctor_patient_link_requests.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(String, ForeignKey("users.id"), nullable=True)  # Who assigned (for admin assignments)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    link_request = relationship("DoctorPatientLinkRequest")


class DoctorReportReview(Base):
    """Doctor's review and validation of AI-generated reports"""
    __tablename__ = "doctor_report_reviews"

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Validation fields
    ai_stage_prediction = Column(Integer, nullable=False)  # Original AI prediction
    doctor_confirmed_stage = Column(Integer, nullable=True)  # Doctor's stage
    stage_override = Column(Boolean, default=False)  # Did doctor change it?
    
    # Clinical notes
    clinical_notes = Column(Text, nullable=True)
    symptoms_description = Column(Text, nullable=True)
    
    # Review status
    reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    report = relationship("DiagnosisReport")
    doctor = relationship("User")


class DoctorCustomRecommendation(Base):
    """Custom recommendations added/edited by doctors"""
    __tablename__ = "doctor_custom_recommendations"

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Recommendation content
    category = Column(String, nullable=False)  # exercise, speech_therapy, medication, etc.
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String, nullable=False)  # low, medium, high, urgent
    
    # Tracking
    is_approved_ai = Column(Boolean, default=False)  # Is this an approved AI rec?
    ai_recommendation_id = Column(String, nullable=True)  # Link to original AI rec
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    report = relationship("DiagnosisReport")
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])


class PatientProgressTracking(Base):
    """Track patient progression over time"""
    __tablename__ = "patient_progress_tracking"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Metrics tracking
    stage = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    tremor_score = Column(Float, nullable=True)
    rigidity_score = Column(Float, nullable=True)
    speech_score = Column(Float, nullable=True)
    handwriting_score = Column(Float, nullable=True)
    
    # Clinical observations
    clinical_observations = Column(Text, nullable=True)
    improvement_noted = Column(Boolean, nullable=True)
    deterioration_noted = Column(Boolean, nullable=True)
    
    tracked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    report = relationship("DiagnosisReport")
    doctor = relationship("User", foreign_keys=[doctor_id])


class DoctorPatientMessage(Base):
    """Secure messaging between doctors and patients"""
    __tablename__ = "doctor_patient_messages"

    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=True)  # Optional context
    
    # Message content
    subject = Column(String, nullable=True)
    message_text = Column(Text, nullable=False)
    message_type = Column(String, default="general")  # general, follow_up, urgent, instruction
    
    # Attachments
    attachment_url = Column(String, nullable=True)
    attachment_name = Column(String, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    report = relationship("DiagnosisReport")


class CaseFlagEnum(enum.Enum):
    """Types of case flags"""
    URGENT_VISIT = "urgent_visit"
    MISCLASSIFICATION = "possible_misclassification"
    FURTHER_TESTS = "needs_further_tests"
    RAPID_PROGRESSION = "rapid_progression"
    ANOMALY_DETECTED = "anomaly_detected"


class HighRiskCaseFlag(Base):
    """Flags for high-risk or special attention cases"""
    __tablename__ = "high_risk_case_flags"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_id = Column(String, ForeignKey("diagnosis_reports.id"), nullable=True)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Flag details
    flag_type = Column(Enum(CaseFlagEnum), nullable=False)
    severity = Column(String, nullable=False)  # low, medium, high, critical
    reason = Column(Text, nullable=False)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    report = relationship("DiagnosisReport")
    doctor = relationship("User", foreign_keys=[doctor_id])