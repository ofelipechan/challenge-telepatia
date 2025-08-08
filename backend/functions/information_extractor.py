import json
from firebase_functions import firestore_fn
from firebase_admin import firestore
from google.cloud.firestore import DocumentSnapshot


@firestore_fn.on_document_created(document="transcriptions/{session_id}")
def information_extractor(event: firestore_fn.Event[DocumentSnapshot]) -> None:
    """
    Firebase function triggered when a transcription document is created in Firestore.
    
    This function receives the transcription data and should extract medical information.
    For now, it only prints the received value as requested.
    """
    try:
        # Get the document data
        session_id = event.params.get("session_id")
        assert session_id, "Session ID is required"
        print(f"Information extractor triggered for session: {session_id}")
        document_data = event.data.to_dict() if event.data else {}
        
        # Update the document status to indicate processing started
        set_processing_status(session_id, "processing_information_extraction")

        # TODO: Implement medical information extraction logic here
        # For now, just print the received value as requested
        
        print('information extraction complete')
        
    except Exception as e:
        print(f"Error in information_extractor: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, "error_extracting_information", str(e))
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")

def set_processing_status(session_id: str, status: str, error_message: str = "") -> None:
    db = firestore.client()
    doc_ref = db.collection('transcriptions').document(session_id)
    doc_ref.update({
        "status": status,
        "error_message": error_message,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Updated status for session {session_id}")
