from typing import List, Optional, Dict, Any
from pydantic import Field, BaseModel
from models.medical_extraction import MedicalExtraction
from datetime import datetime

class DiagnosisProbability(BaseModel):
    """
    Diagnosis Probability model.
    This model is used to store probable Diagnoses for a patient.
    """
    name: str = Field(description="The disease name")
    probability: Optional[float] = Field(default=None, description="The probability of the patient having the disease")
    reasoning: Optional[str] = Field(default=None, description="The reasoning for the diagnosis probability")
    symptoms: Optional[List[str]] = Field(default=None, description="The symptoms the patient has that are related to the disease")

class ClassifiedSymptoms(BaseModel):
    name: str = Field(description="The symptom name")
    intensity: Optional[str] = Field(description="Intensity: mild, moderate, severe, critical")
    severity: Optional[str] = Field(description="Severity: mild, moderate, severe, critical")
    duration: Optional[str] = Field(description="How long the symptom has persisted")
    confidence_score: float = Field(description="Confidence score for the severity classification (0-1)")

class ClinicalRecord(MedicalExtraction):
    """
    Database Model representing a clinical record.
    """
    session_id: str
    classified_symptoms: Optional[List[ClassifiedSymptoms]] = Field(description="List of symptoms")
    diagnosis_report: Optional[str] = Field(default=None, description="The diagnosis report")
    diagnosis: Optional[List[DiagnosisProbability]] = Field(default=None, description="List probable diagnoses")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the transcription was last updated")
