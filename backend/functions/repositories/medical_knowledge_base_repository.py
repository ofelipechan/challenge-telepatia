from importlib import metadata
import os
from glob import glob
from typing import List
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from repositories.documents.medical_documents import get_medical_documents
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

host = os.getenv("PINECONE_HOST")
index_name = os.getenv("PINECONE_INDEX_NAME")
api_key = os.getenv("PINECONE_API_KEY")
assert host, "Missing PINECONE_HOST env variable"
assert api_key, "Missing PINECONE_API_KEY env variable"
assert index_name, "Missing PINECONE_INDEX_NAME env variable"

BASE_DIR = os.path.dirname(__file__)
docs_folder_path = os.path.join(BASE_DIR, "documents")


class MedicalKnowledgeRepository:
    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vectorstore = PineconeVectorStore(
            index_name=index_name, embedding=self.embeddings, host=host
        )

    def load_documents(self):
        """Populate the medical knowledge base with documents."""
        try:
            print("loading documents")
            docs = self.read_local_documents()

            pc = Pinecone()

            if index_name not in pc.list_indexes().names():
                print(f"creating index {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=3072,  # matches OpenAI text-embedding-3-large
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                self.vectorstore = PineconeVectorStore(
                    index_name=index_name, embedding=self.embeddings, host=host
                )
            print("creating splitter")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=150
            )
            print("generating chunks and adding to vectorstore")
            for doc in docs:
                chunks = splitter.split_documents([doc])
                self.vectorstore.add_documents(chunks)
                print(
                    f"Inserted: {doc.metadata['disease_name']} ({len(chunks)} chunks)"
                )
        except Exception as e:
            print(f"error when trying to add documents to vectorstore: {e}")

    def read_local_documents(self):
        print("reading documents locally")
        docs = []
        for file_path in glob(os.path.join(docs_folder_path, "*.md")):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            disease_name = os.path.splitext(os.path.basename(file_path))[0]
            docs.append(Document(page_content=text, metadata={"disease_name": disease_name}))
        print(f"Loaded {len(docs)} markdown documents from {docs_folder_path}")
        return docs

    def get_index_stats(self):
        """Verify if vector store exists"""
        index = self.vectorstore.get_pinecone_index(index_name)
        if not index:
            print("index does not exist")
            return None
        stats = index.describe_index_stats()
        return {
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness,
            "total_vector_count": stats.total_vector_count,
        }

    def similarity_search(self, query: str, top_k=10) -> List[Document]:
        """Search the medical knowledge base for relevant documents."""
        docs = self.vectorstore.similarity_search(query=query, k=top_k)
        sorted_docs = sorted(docs, key=lambda d: d.metadata.get('disease_name'))
        return sorted_docs

    def retrieve_full_docs(self, query: str, top_k=3) -> List[Document]:
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        matches = retriever.invoke(query)

        # Collect unique disease_names from matches
        disease_names = {m.metadata["disease_name"] for m in matches}

        # Load full documents from filesystem based on disease_names
        full_docs = []
        for disease_name in disease_names:
            file_path = os.path.join(docs_folder_path, f"{disease_name}.md")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    full_docs.append(
                        Document(
                            page_content=f.read(),
                            metadata={"disease_name": disease_name},
                        )
                    )
            else:
                print(f"Warning: Document file not found for disease: {disease_name}")

        return full_docs
