from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class QueueStatus(str, Enum):
    """
    Enum for transcription processing status.
    """
    WAITING = "waiting"
    FINISHED = "finished"
    ERROR = "error"

class Queue(BaseModel):
    """
    Database Model representing a queue.
    """
    session_id: str = Field(..., description="Unique session ID for the process")
    audio_url: str = Field(..., description="The URL of the audio file to be transcribed")
    status: Optional[QueueStatus] = Field(default=QueueStatus.WAITING, description="transcription status")
    created_at: Optional[datetime] = Field(default=None, description="date created")