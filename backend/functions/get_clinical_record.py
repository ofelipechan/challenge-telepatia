import json
from firebase_functions import https_fn
from firebase_admin import firestore
from models.clinical_record import ClinicalRecord

def handle_cors_preflight(req) -> https_fn.Response | None:
    """Handle CORS preflight requests."""
    if req.method == "OPTIONS":
        return https_fn.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    return None

def get_session_id_from_query(req: https_fn.Request) -> str:
    """Extract session_id from query parameters."""
    session_id = req.args.get("session_id")
    if not session_id:
        raise ValueError("session_id parameter is required")
    return session_id

def retrieve_clinical_record(session_id: str) -> dict:
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

@https_fn.on_request()
def get_clinical_record(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase function to retrieve clinical record data by session_id.
    
    Query parameters:
    - session_id: The unique session identifier
    
    Returns:
    - Clinical record data including symptoms, diagnosis, and treatment plan
    """
    try:
        print('Retrieving clinical record')
        
        cors_response = handle_cors_preflight(req)
        if cors_response:
            return cors_response
            
        if req.method != "GET":
            return https_fn.Response(
                status=405,
                response=json.dumps({"error": "Method not allowed. Only GET requests are supported."}),
                headers={"Content-Type": "application/json"}
            )
        
        # Extract session_id from query parameters
        try:
            session_id = get_session_id_from_query(req)
        except ValueError as e:
            return https_fn.Response(
                status=400,
                response=json.dumps({"error": str(e)}),
                headers={"Content-Type": "application/json"}
            )
        
        # Retrieve clinical record data from Firestore
        try:
            clinical_record_data = retrieve_clinical_record(session_id)
        except ValueError as e:
            return https_fn.Response(
                status=404,
                response=json.dumps({"error": str(e)}),
                headers={"Content-Type": "application/json"}
            )
        
        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "data": clinical_record_data
            }),
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        print(f"Error in clinical_record_handler: {str(e)}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers={"Content-Type": "application/json"}
        )
