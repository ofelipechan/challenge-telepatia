from firebase_functions import https_fn

@https_fn.on_request()
def transcription_function(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("this is the transcription function")