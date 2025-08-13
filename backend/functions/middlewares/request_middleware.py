from functools import wraps
from typing import Callable, Union, List
from firebase_functions import https_fn
import json

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def with_cors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(req: https_fn.Request) -> https_fn.Response:
        # Handle CORS preflight
        if req.method == "OPTIONS":
            return https_fn.Response(
                status=200,
                headers=CORS_HEADERS
            )
        return func(req)
    return wrapper

def with_methods(allowed_methods: Union[str, List[str]]) -> Callable:
    """
    Validation middleware decorator that accepts specific HTTP methods.
    
    Args:
        allowed_methods: Single method string or list of allowed methods
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(req: https_fn.Request) -> https_fn.Response:
            # Convert to list if single method provided
            methods = allowed_methods if isinstance(allowed_methods, list) else [allowed_methods]
            
            if req.method not in methods:
                return https_fn.Response(
                    status=405,
                    response=json.dumps({
                        "error": f"Method not allowed."
                    }),
                    headers={"Content-Type": "application/json"}
                )
            return func(req)
        return wrapper
    return decorator