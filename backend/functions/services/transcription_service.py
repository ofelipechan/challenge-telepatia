

import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

from repositories.transcription_repository import save_transcription
from models.transcription import Transcription, TranscriptionStatus

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)

def generate_transcription(audio_url: str, session_id: str) -> Transcription:
    audio_file: io.BytesIO = download_audio(audio_url, session_id)
    transcription_result = transcribe_audio(audio_file)
    transcription = Transcription(
            session_id=session_id,
            audio_url=audio_url,
            text=transcription_result["text"],
            language=transcription_result["language"],
            duration=transcription_result["duration"],
            context=transcription_result["context"],
            status=TranscriptionStatus.TRANSCRIPTION_FINISHED.value
    )
    save_transcription(transcription)

    return transcription

def download_audio(audio_url: str, session_id: str) -> io.BytesIO:
    print(f"Downloading audio from: {audio_url}")
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()
    content: bytes = response.content
    audio_file = io.BytesIO(content)
    audio_file.name = f"audio_{session_id}.mp3"
    print(f"audio downloaded for session {session_id}")
    return audio_file


def transcribe_audio(audio_file: io.BytesIO):
    print("transcribing audio...")
    medical_context = "Medical consultation recording. It may contain technical medical terminology, patient symptoms, diagnosis, treatment plan, medications, or clinical observations."

    # mocked for testing
    transcription_params = {
        "file": audio_file,
        "model": "whisper-1",
        "response_format": "verbose_json",
        "prompt": medical_context,
        "temperature": 0.0,
    }

    response = openai_client.audio.transcriptions.create(**transcription_params)
    print("transcription generation finished")

    return {
        "text": response.text,
        "language": response.language,
        # "segments": segments,
        "duration": response.duration,
        "context": medical_context,
    }
