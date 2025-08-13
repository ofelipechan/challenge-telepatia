# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app
from audio_transcription import transcription_handler
from medical_information_extractor import information_extractor_handler
from diagnosis_generation import diagnosis_generation_handler
from get_transcription_status import get_transcription
from get_clinical_record import get_clinical_record

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)

initialize_app()

# Export the functions properly
__all__ = [
    "transcription_handler",
    "information_extractor_handler",
    "diagnosis_generation_handler",
    "get_transcription",
    "get_clinical_record"
]

@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")