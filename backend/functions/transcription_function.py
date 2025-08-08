import os
import requests
import json
import io
import uuid
from datetime import datetime
from firebase_functions import https_fn
from firebase_admin import firestore
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)

def handle_cors_preflight(req) -> https_fn.Response | None:
    if req.method == "OPTIONS":
        return https_fn.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    return None

def get_request_data(request_data: dict) -> str:
    if not request_data:
        raise ValueError("No JSON data provided")
    
    audio_url = request_data.get("audio_url")
    
    if not audio_url:
        raise ValueError("audio_url is required")
    
    return audio_url

def generate_session_id() -> str:
    """Generate a unique session ID using UUID4."""
    return str(uuid.uuid4())


@https_fn.on_request()
def transcription_handler(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase function to transcribe audio from a URL.
    
    Expected request body:
    {
        "audio_url": "https://example.com/audio.mp3"
    }
    
    Returns:
    {
        "session_id": "auto-generated-uuid",
        "status": "transcribed"
    }
    """
    try:
        print('starting transcription')

        cors_response = handle_cors_preflight(req)
        if cors_response:
            return cors_response
            
        if req.method != "POST":
            return https_fn.Response(
                status=405,
                response=json.dumps({"error": "Method not allowed"}),
                headers={"Content-Type": "application/json"}
            )
        
        request_data = req.get_json()
        audio_url = get_request_data(request_data)
        session_id = generate_session_id()
        aduio_file: io.BytesIO = download_audio(audio_url, session_id)        
        transcription_object = transcribe_audio(aduio_file)
        
        save_to_filestore(session_id, audio_url, transcription_object)
        
        return https_fn.Response(
            status=200,
            response=json.dumps({
                "session_id": session_id,
                "status": "transcribed"
            }),
            headers={"Content-Type": "application/json"}
        )
    
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return https_fn.Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            headers={"Content-Type": "application/json"}
        )
    
    except requests.RequestException as e:
        print(f"Error downloading audio: {str(e)}")
        return https_fn.Response(
            status=400,
            response=json.dumps({"error": f"Failed to download audio file: {str(e)}"}),
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        print(f"Error in transcription function: {str(e)}")
        return https_fn.Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            headers={"Content-Type": "application/json"}
        )


def download_audio(audio_url: str, session_id: str) -> io.BytesIO:
    print(f"Downloading audio from: {audio_url}")
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()
    content: bytes  = response.content
    audio_file = io.BytesIO(content)
    audio_file.name = f"audio_{session_id}.mp3"
    print(f'audio downloaded for session {session_id}')
    return audio_file

def transcribe_audio(audio_file: io.BytesIO):
    print('starting transcription')
    medical_context = "Medical consultation recording. It may contain technical medical terminology, patient symptoms, diagnosis, treatment plan, medications, or clinical observations."

    
    # mocked for testing
    response = {
        "text": "test",
        "language": "en",
        "duration": 0,
    }
    segments = [{
        "id": "1",
        "start": 0,
        "end": 10,
        "text": "test"
    }]
    return {
        "text": response["text"],
        "language": response["language"],
        "segments": segments,
        "duration": response["duration"],
        "medical_context": medical_context
    }
  
    # transcription_params = {
    #     "file": audio_file,
    #     "model": "whisper-1",
    #     "response_format": "verbose_json",
    #     "timestamp_granularities": ["segment"],
    #     "prompt": medical_context,
    #     "temperature": 0.0,
    # }

    # response = openai_client.audio.transcriptions.create(**transcription_params)
    # print('got openai response')
    # segments = []
    # if response.segments:
    #     for segment in response.segments:
    #         segments.append({
    #             "id": segment.id,
    #             "start": segment.start,
    #             "end": segment.end,
    #             "text": segment.text
    #         })
    
    # return {
    #     "text": response.text,
    #     "language": response.language,
    #     "segments": segments,
    #     "duration": response.duration,
    #     "medical_context": medical_context
    # }

def save_to_filestore(session_id: str, audio_url: str, transcription_object: dict):
    # Save transcription to Firestore to trigger information extraction
    db = firestore.client()
    doc_ref = db.collection('transcriptions').document(session_id)
    
    # Add session metadata to the transcription object
    firestore_data = {
        **transcription_object,
        "session_id": session_id,
        "audio_url": audio_url,
        "created_at": firestore.SERVER_TIMESTAMP,
        "status": "transcribed"
    }
    
    doc_ref.set(firestore_data)
    print(f"Transcription saved to Firestore for session: {session_id}")