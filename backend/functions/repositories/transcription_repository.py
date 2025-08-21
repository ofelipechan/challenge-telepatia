from firebase_admin import firestore
from models.transcription import Transcription, TranscriptionStatus


def save_transcription(transcription: Transcription):
    # Save transcription to Firestore to trigger information extraction
    print(f"Saving transcription for session {transcription.session_id}")

    db = firestore.client()

    doc_ref = db.collection("transcriptions").document(transcription.session_id)

    # Convert Pydantic model to dict and add server timestamp
    transcription_dict = transcription.model_dump()
    transcription_dict["created_at"] = firestore.SERVER_TIMESTAMP
    doc_ref.set(transcription_dict)

    print(
        f"Transcription saved to Firestore for session: {transcription.session_id}"
    )

def get_transcription_by_session_id(session_id: str) -> dict:
    """Retrieve transcription data from Firestore by session_id."""
    # Query the transcriptions collection for the given session_id
    db = firestore.client()

    transcriptions_ref = db.collection("transcriptions")
    query = transcriptions_ref.where("session_id", "==", session_id)
    docs = query.stream()
    
    # Get the first (and should be only) document
    transcription_doc = None
    for doc in docs:
        transcription_doc = doc
        break
    
    if not transcription_doc:
        raise ValueError(f"No transcription found for session_id: {session_id}")
    
    # Convert Firestore document to dictionary
    transcription_data = transcription_doc.to_dict()
    
    # Convert Firestore timestamps to ISO strings for JSON serialization
    if "created_at" in transcription_data and transcription_data["created_at"]:
        transcription_data["created_at"] = transcription_data["created_at"].isoformat()
    if "updated_at" in transcription_data and transcription_data["updated_at"]:
        transcription_data["updated_at"] = transcription_data["updated_at"].isoformat()
    
    return transcription_data

def set_processing_status(session_id: str, status: TranscriptionStatus, error_message: str = "") -> None:
    db = firestore.client()
    doc_ref = db.collection('transcriptions').document(session_id)
    doc_ref.update({
        "status": status.value,
        "error_message": error_message,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Updated session {session_id}. Status: {status}")