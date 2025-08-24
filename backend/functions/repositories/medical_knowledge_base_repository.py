import os
from typing import List
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from repositories.documents.medical_documents import get_medical_documents

load_dotenv()

host = os.getenv("PINECONE_HOST")
index_name = os.getenv("PINECONE_INDEX_NAME")
api_key = os.getenv("PINECONE_API_KEY")
assert host, "Missing PINECONE_HOST env variable"
assert api_key, "Missing PINECONE_API_KEY env variable"
assert index_name, "missing PINECONE_INDEX_NAME env variable"

class MedicalKnowledgeRepository:
    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = PineconeVectorStore(index_name=index_name, embedding=self.embeddings, host=host)
    
    def load_documents(self) -> List[str]:
        """Populate the medical knowledge base with documents."""
        try:
            print('loading documents')
            medical_documents = get_medical_documents()
            print('adding documents')
            ids = self.vectorstore.add_documents(medical_documents)
            print('documents added')
            print(ids)
            return ids
        except Exception as e:
            print(f'error when trying to add documents to vectorstore: {e}')
    
    def get_index_stats(self):
        """Verify if vector store exists"""
        index = self.vectorstore.get_pinecone_index(index_name)
        if not index:
            print('index does not exist')
            return None
        stats = index.describe_index_stats()
        return {
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness,
            "total_vector_count": stats.total_vector_count
        }

    def similarity_search(self, query: str) -> List[Document]:
        """Search the medical knowledge base for relevant documents."""
        result = self.vectorstore.similarity_search(query)
        return result

        
