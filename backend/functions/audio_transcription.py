from google.cloud.firestore import DocumentSnapshot
from firebase_functions import firestore_fn
from services.transcription_service import generate_transcription
from filestore.queue_repository import set_queue_processing_status
from models.queue import Queue, QueueStatus

def get_request_data(request_data: dict) -> tuple[str, str]:
    if not request_data:
        raise ValueError("No JSON data provided")

    audio_url = request_data.get("audio_url")
    transcription_text = request_data.get("transcription_text")

    if not audio_url and not transcription_text:
        raise ValueError("either audio_url or transcription_text must be provided")

    return audio_url, transcription_text

@firestore_fn.on_document_created(
    document="queue/{session_id}",
    timeout_sec=300  # 5 minutes
)
def transcription_handler(event: firestore_fn.Event[DocumentSnapshot]) -> None:
    """
    Firebase function to transcribe audio.
    """
    try:
        print("starting transcription")

        session_id = event.params.get("session_id")
        assert session_id, "Session ID is required"
        if event.data:
            data_dict = event.data.to_dict()
            queue = Queue(**data_dict)
        else:
            print("Empty object provided on function invoke")
            return

        generate_transcription(queue.audio_url, session_id)

        set_queue_processing_status(session_id, QueueStatus.FINISHED)
    except Exception as e:
        print('An error occured while executing transcription function')
        if session_id:
            set_queue_processing_status(session_id, QueueStatus.ERROR)
        raise e
