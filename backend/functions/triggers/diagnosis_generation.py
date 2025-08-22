
from firebase_functions import firestore_fn
from google.cloud.firestore import DocumentSnapshot
from services.diagnosis_generation_service import DiagnosisGenerationService
from repositories.transcription_repository import set_processing_status
from models.clinical_record import ClinicalRecord
from models.transcription import TranscriptionStatus

@firestore_fn.on_document_created(
    document="clinical_record/{session_id}",
    timeout_sec=300  # 5 minutes
)
def diagnosis_generation_handler(event: firestore_fn.Event[DocumentSnapshot]) -> None:
    """
    Firebase function triggered when a clinical record document is created in Firestore.
    
    This function receives the clinical record data and should generate a diagnosis.
    """
    try:
        # Get the document data
        session_id = event.params.get("session_id")
        assert session_id, "Session ID is required"
        print(f"Diagnosis generation triggered for session: {session_id}")
        if event.data:
            data_dict = event.data.to_dict()
            clinical_record = ClinicalRecord(**data_dict)
        else:
            print("Empty object provided on function invoke")
            raise ValueError("Empty object provided on function invoke")
        diagnosis_generation_service = DiagnosisGenerationService()
        diagnosis_generation_service.process(clinical_record)
        print('Diagnosis generation complete')
    except Exception as e:
        print(f"Error in diagnosis_generation: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, TranscriptionStatus.DIAGNOSIS_ERROR, str(e))
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")


