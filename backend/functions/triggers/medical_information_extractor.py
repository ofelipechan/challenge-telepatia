from firebase_functions import firestore_fn
from google.cloud.firestore import DocumentSnapshot
from repositories.transcription_repository import set_processing_status
from models.transcription import Transcription, TranscriptionStatus
from services.medical_info_extractor_service import MedicalInfoExtractor

@firestore_fn.on_document_created(document="transcriptions/{session_id}")
def information_extractor_handler(event: firestore_fn.Event[DocumentSnapshot]) -> None:
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
        if event.data:
            data_dict = event.data.to_dict()
            transcription = Transcription(**data_dict)
        else:
            print("Empty object provided on function invoke")
            return
        
        medical_info_extractor = MedicalInfoExtractor()
        medical_info_extractor.process(transcription)
        
        print('information extraction complete')
    except Exception as e:
        print(f"Error in information_extractor: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, TranscriptionStatus.TRANSCRIPTION_ERROR, str(e))
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")
