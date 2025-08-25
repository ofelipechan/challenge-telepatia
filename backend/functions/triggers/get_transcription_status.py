import json
from firebase_functions import https_fn
from utils.request_utils import get_query_params
from middlewares.request_middleware import with_cors, with_methods, CORS_HEADERS
from repositories.transcription_repository import get_transcription_by_session_id

@https_fn.on_request()
@with_cors
@with_methods(["GET"])
def get_transcription(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase function to retrieve transcription status and data by session_id.
    
    Query parameters:
    - session_id: The unique session identifier
    
    Returns:
    - Transcription data including status, text, and metadata
    """
    try:
        print('Retrieving transcription status')
      
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
        
        # Retrieve transcription data from Firestore
        transcription_data = get_transcription_by_session_id(session_id)

        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "data": transcription_data
            }),
            headers=CORS_HEADERS
        )
        
    except Exception as e:
        print(f"Error in transcription_status_handler: {str(e)}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )

