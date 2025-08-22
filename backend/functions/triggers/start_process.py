import os
import requests
import json
import uuid
from firebase_functions import https_fn
from firebase_admin import firestore
from dotenv import load_dotenv
from models.transcription import Transcription, TranscriptionStatus
from middlewares.request_middleware import with_cors, with_methods, CORS_HEADERS
from repositories.transcription_repository import save_transcription
from repositories.queue_repository import add_to_queue
from models.queue import Queue

load_dotenv()

def get_request_data(request_data: dict) -> str:
    if not request_data:
        raise ValueError("No JSON data provided")

    audio_url = request_data.get("audio_url")
    transcription_text = request_data.get("transcription_text")

    if not audio_url and not transcription_text:
        raise ValueError("either audio_url or transcription_text must be provided")

    return audio_url, transcription_text


def generate_session_id() -> str:
    """Generate a unique session ID using UUID4."""
    return str(uuid.uuid4())


@https_fn.on_request()
@with_cors
@with_methods(["POST"])
def start_process(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase function to transcribe audio from a URL.

    request body:
    {
        "audio_url": "https://example.com/audio.mp3",
        "transcription_text": "The transcription text of the audio"
    }

    """
    try:
        print("starting transcription")

        request_data = req.get_json()
        audio_url, transcription_text = get_request_data(request_data)
        session_id: str = generate_session_id()

        if audio_url:
            # add to transcriptino queue
            add_to_queue(Queue(session_id=session_id, audio_url=audio_url))
            return https_fn.Response(
                status=200,
                response=json.dumps({"session_id": session_id, "status": TranscriptionStatus.TRANSCRIPTION_WAITING }),
                headers=CORS_HEADERS,
            )

        # transcription already provided
        transcription = Transcription(
            session_id=session_id,
            text=transcription_text,
            audio_url=audio_url,
            status=TranscriptionStatus.TRANSCRIPTION_FINISHED.value
        )
        save_transcription(transcription)
        return https_fn.Response(
            status=200,
            response=json.dumps({"session_id": session_id, "status": TranscriptionStatus.TRANSCRIPTION_FINISHED }),
            headers=CORS_HEADERS,
        )
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return https_fn.Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"},
        )

    except requests.RequestException as e:
        print(f"Error downloading audio: {str(e)}")
        return https_fn.Response(
            status=400,
            response=json.dumps({"error": f"Failed to download audio file: {str(e)}"}),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"Error in transcription function: {str(e)}")
        return https_fn.Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            headers={"Content-Type": "application/json"},
        )



