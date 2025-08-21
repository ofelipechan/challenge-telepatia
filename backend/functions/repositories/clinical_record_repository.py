from firebase_admin import firestore
from models.clinical_record import ClinicalRecord

def save_clinical_record(clinical_record: ClinicalRecord):
    print('Saving clinical record')
    db = firestore.client()
    doc_ref = db.collection('clinical_record').document(clinical_record.session_id)
    
    doc_ref.set(clinical_record.model_dump())
    print(f"Clinical Record saved to Firestore for session: {clinical_record.session_id}")
