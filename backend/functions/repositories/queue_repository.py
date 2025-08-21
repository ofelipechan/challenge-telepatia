from firebase_admin import firestore
from models.queue import Queue, QueueStatus


def add_to_queue(queue: Queue):
    # Save transcription to Firestore to trigger information extraction
    db = firestore.client()

    print(f"Adding audio to queue for session: {queue.session_id}")
    doc_ref = db.collection("queue").document(queue.session_id)

    # Convert to dict and add SERVER_TIMESTAMP separately
    queue_data = queue.model_dump()
    queue_data["created_at"] = firestore.SERVER_TIMESTAMP
    
    doc_ref.set(queue_data)
    print(
        f"Audio added to transcription queue for session: {queue.session_id}"
    )

def set_queue_processing_status(session_id: str, status: QueueStatus, error_message: str = "") -> None:
    print(f"Updating queue status of {status} for session {session_id}")
    db = firestore.client()
    doc_ref = db.collection('queue').document(session_id)
    doc_ref.update({
        "status": status.value,
        "error_message": error_message,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Updated status for session {session_id}")