from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from firebase_admin import firestore

class TranscriptionStatus(str, Enum):
    """
    Enum for transcription processing status.
    """
    TRANSCRIPTION_FINISHED = "transcription_finished"
    TRANSCRIPTION_ERROR = "transcription_error"
    DIAGNOSIS_STARTED = "diagnosis_started"
    DIAGNOSIS_FINISHED = "diagnosis_finished"
    DIAGNOSIS_ERROR = "diagnosis_error"
    INFORMATION_EXTRACTION_STARTED = "information_extraction_started"
    INFORMATION_EXTRACTION_FINISHED = "information_extraction_finished"
    INFORMATION_EXTRACTION_ERROR = "information_extraction_error"

class Transcription(BaseModel):
    """
    Database Model representing a transcription.
    """
    session_id: str
    audio_url: Optional[str] = Field(default=None, description="URL of the audio file")
    text: Optional[str] = Field(description="transcription in text")
    context: Optional[str] = Field(default=None, description="Additional context or notes about the transcription")
    duration: Optional[float] = Field(default=None, description="Duration of the audio file in seconds")
    status: Optional[TranscriptionStatus] = Field(default=None, description="Current status of the transcription process")
    error_message: Optional[str] = Field(default=None, description="Error message if transcription failed")
    created_at: datetime = firestore.SERVER_TIMESTAMP
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the transcription was last updated")
