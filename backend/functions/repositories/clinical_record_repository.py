from firebase_admin import firestore
from models.clinical_record import ClinicalRecord, ReportOutput

def save_clinical_record(clinical_record: ClinicalRecord):
    print('Saving clinical record')
    db = firestore.client()
    doc_ref = db.collection('clinical_record').document(clinical_record.session_id)
    
    doc_ref.set(clinical_record.model_dump())
    print(f"Clinical Record saved to Firestore for session: {clinical_record.session_id}")

def save_diagnosis_report(session_id: str, diagnosis: ReportOutput) -> None:
    """
    Save the diagnosis report to Firestore.
    """
    print(f'Saving diagnosis report for session: {session_id}')
    db = firestore.client()
    doc_ref = db.collection('clinical_record').document(session_id)
    
    doc_ref.update({
        "diagnosis_report": diagnosis.report,
        "diagnosis": [d.model_dump() for d in diagnosis.diagnosis_probabilities],
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Diagnosis report saved to Firestore for session: {session_id}")

def get_clinical_record_by_session(session_id: str) -> dict:
    """Retrieve clinical record data from Firestore by session_id."""
    db = firestore.client()
    
    # Query the clinical_records collection for the given session_id
    clinical_records_ref = db.collection("clinical_record")
    query = clinical_records_ref.where("session_id", "==", session_id)
    docs = query.stream()
    
    # Get the first (and should be only) document
    clinical_record_doc = None
    for doc in docs:
        clinical_record_doc = doc
        break
    
    if not clinical_record_doc:
        raise ValueError(f"No clinical record found for session_id: {session_id}")
    
    # Convert Firestore document to dictionary
    clinical_record_data = clinical_record_doc.to_dict()
    
    # Convert Firestore timestamps to ISO strings for JSON serialization
    if "created_at" in clinical_record_data and clinical_record_data["created_at"]:
        clinical_record_data["created_at"] = clinical_record_data["created_at"].isoformat()
    if "updated_at" in clinical_record_data and clinical_record_data["updated_at"]:
        clinical_record_data["updated_at"] = clinical_record_data["updated_at"].isoformat()
    
    return clinical_record_data