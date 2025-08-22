from typing import List
from firebase_functions import https_fn

def get_query_params(req: https_fn.Request, params: List[str]) -> dict:
    """Extract from query parameters."""
    extracted = {}
    for param in params:
        value = req.args.get(param)
        extracted[param] = value

    return extracted