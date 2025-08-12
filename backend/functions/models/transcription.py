from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from firebase_admin import firestore

class Transcription(BaseModel):
    """
    Database Model representing a transcription.
    """
    session_id: str
    audio_url: str
    text: Optional[str] = Field(description="transcription in text")
    context: Optional[str] = Field(default=None, description="Additional context or notes about the transcription")
    duration: Optional[float] = Field(default=None, description="Duration of the audio file in seconds")
    status: Optional[str] = Field(default=None, description="Current status of the transcription process")
    error_message: Optional[str] = Field(default=None, description="Error message if transcription failed")
    created_at: datetime = firestore.SERVER_TIMESTAMP
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the transcription was last updated")
