import json
from firebase_functions import https_fn
from middlewares.request_middleware import CORS_HEADERS, with_cors, with_methods
from repositories.medical_knowledge_base_repository import MedicalKnowledgeRepository

@https_fn.on_request()
@with_cors
@with_methods(["POST"])
def load_documents(req: https_fn.Request) -> https_fn.Response:
    try:
        repository = MedicalKnowledgeRepository()
        repository.load_documents()
        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True
            }),
            headers=CORS_HEADERS
        )
    except Exception as e:
        print(f"an error occurred while creating vector db: {e}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )

@https_fn.on_request()
@with_cors
@with_methods(["GET"])
def get_index_stats(req: https_fn.Request) -> https_fn.Response:
    try:
        repository = MedicalKnowledgeRepository()
        index_stats = repository.get_index_stats()
        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "index_stats": index_stats
            }),
            headers=CORS_HEADERS
        )
    except Exception as e:
        print(f"an error occurred while creating vector db: {e}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )

@https_fn.on_request()
@with_cors
@with_methods(["POST"])
def query_documents(req: https_fn.Request) -> https_fn.Response:
    try:
        request_data = req.get_json()
        query = request_data.get("query")
        if not query:
            raise ValueError("missing query")

        repository = MedicalKnowledgeRepository()
        documents = repository.retrieve_full_docs(query)

        documents_list = []
        for doc in documents:
            documents_list.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })

        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "documents": documents_list
            }),
            headers=CORS_HEADERS
        )
    except Exception as e:
        print(f"an error occurred while creating vector db: {e}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )

@https_fn.on_request()
@with_cors
@with_methods(["POST"])
def similarity_search(req: https_fn.Request) -> https_fn.Response:
    try:
        request_data = req.get_json()
        query = request_data.get("query")
        if not query:
            raise ValueError("missing query")

        repository = MedicalKnowledgeRepository()
        documents = repository.similarity_search(query)

        documents_list = []
        for doc in documents:
            documents_list.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })

        return https_fn.Response(
            status=200,
            response=json.dumps({
                "success": True,
                "documents": documents_list
            }),
            headers=CORS_HEADERS
        )
    except Exception as e:
        print(f"an error occurred while creating vector db: {e}")
        return https_fn.Response(
            status=500,
            response=json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            headers=CORS_HEADERS
        )