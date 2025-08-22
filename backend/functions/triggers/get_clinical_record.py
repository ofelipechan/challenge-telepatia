import json
from firebase_functions import https_fn
from repositories.clinical_record_repository import get_clinical_record_by_session
from utils.request_utils import get_query_params
from middlewares.request_middleware import with_cors, with_methods, CORS_HEADERS

@https_fn.on_request()
@with_cors
@with_methods(["GET"])
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
        
        # Extract session_id from query parameters
        try:
            params = get_query_params(req, ["session_id"])
            session_id = params["session_id"]
            if not session_id:
                raise ValueError("session_id not provided")
        except ValueError as e:
            return https_fn.Response(
                status=400,
                response=json.dumps({"error": str(e)}),
                headers=CORS_HEADERS
            )
        
        # Retrieve clinical record data from Firestore
        try:
            clinical_record_data = get_clinical_record_by_session(session_id)
        except ValueError as e:
            return https_fn.Response(
                status=404,
                response=json.dumps({"error": str(e)}),
                headers=CORS_HEADERS
            )
        
        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "data": clinical_record_data
            }),
            headers=CORS_HEADERS
        )
        
    except Exception as e:
        print(f"Error in clinical_record_handler: {str(e)}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )
