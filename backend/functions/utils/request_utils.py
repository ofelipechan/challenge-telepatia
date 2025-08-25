from typing import List
from firebase_functions import https_fn

def get_query_params(req: https_fn.Request, params: List[str]) -> dict:
    """
    Extract specified query parameters from the HTTP request and return them as a dictionary.

    Args:
        req (https_fn.Request): The HTTP request object containing query parameters.
        params (List[str]): A list of parameter names to extract from the query string.

    Returns:
        dict: A dictionary mapping each parameter name to its value (or None if not present).
    """
    extracted = {}
    for param in params:
        value = req.args.get(param)
        extracted[param] = value

    return extracted