import os
import requests
import json
import io
import uuid
from firebase_functions import https_fn
from firebase_admin import firestore
from openai import OpenAI
from dotenv import load_dotenv
from models.transcription import Transcription
from middlewares.request_middleware import with_cors, with_methods, CORS_HEADERS

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)


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
def transcription_handler(req: https_fn.Request) -> https_fn.Response:
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
            aduio_file: io.BytesIO = download_audio(audio_url, session_id)
            transcription_result = transcribe_audio(aduio_file)
        else:
            transcription_result = {"text": transcription_text}

        transcription: Transcription = {
            **transcription_result,
            "session_id": session_id,
            "audio_url": audio_url,
            "status": "transcribed",
            "created_at": firestore.SERVER_TIMESTAMP,
        }

        print("Saving transcription")
        save_to_filestore(transcription)

        return https_fn.Response(
            status=200,
            response=json.dumps({"session_id": session_id, "status": "transcribed"}),
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
    print("starting transcription")
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
    print("got openai response")

    return {
        "text": response.text,
        "language": response.language,
        # "segments": segments,
        "duration": response.duration,
        "context": medical_context,
    }


def save_to_filestore(transcription: Transcription):
    # Save transcription to Firestore to trigger information extraction
    db = firestore.client()
    doc_ref = db.collection("transcriptions").document(transcription["session_id"])

    doc_ref.set(transcription)
    print(
        f"Transcription saved to Firestore for session: {transcription["session_id"]}"
    )
