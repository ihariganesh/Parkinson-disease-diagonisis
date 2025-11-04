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
    date_of_birth = Column(DateTime, nullable=True)
    phone_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    medical_data = relationship("MedicalData", back_populates="patient")
    patient_reports = relationship("DiagnosisReport", foreign_keys="DiagnosisReport.patient_id", back_populates="patient")
    doctor_reports = relationship("DiagnosisReport", foreign_keys="DiagnosisReport.doctor_id", back_populates="doctor")


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