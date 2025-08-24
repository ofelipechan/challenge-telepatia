from pydantic import BaseModel, Field
from typing import List, Optional

class PatientInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Patient's full name")
    age: Optional[int] = Field(default=None, description="Patient's age in years")
    id_number: Optional[str] = Field(default=None, description="Patient ID or medical record number")
    date_of_birth: Optional[str] = Field(default=None, description="Patient's date of birth")
    gender: Optional[str] = Field(default=None, description="Patient's gender")
    nationality: Optional[str] = Field(default=None, description="Patient's nationality")

class Symptom(BaseModel):
    name: str = Field(description="The symptom name")
    duration: Optional[str] = Field(description="How long the symptom have persisted")
    intensity: Optional[str] = Field(description="How intense is the symptom presented by the patient")

class MedicalExtraction(BaseModel):
    summary: Optional[str] = Field(description="A short summary of what the transcription is about")
    patient_info: Optional[PatientInfo] = Field(description="Patient identification information")
    symptoms: Optional[List[Symptom]] = Field(description="List of symptoms mentioned")
    reason_for_visit: Optional[str] = Field(description="Main reason for the medical visit")
