"""
Vector Store Service
Manages FAISS vector store for HR policy documents using Mistral AI embeddings
"""
import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings

from services.document_loader import HRDocumentLoader


class HRVectorStore:
    """Vector store for HR policy documents"""

    def __init__(self, mistral_api_key: str, vector_store_path: str, policies_path: str):
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            mistral_api_key=mistral_api_key
        )
        self.vector_store_path = vector_store_path
        self.policies_path = policies_path
        self.vector_store: Optional[FAISS] = None

        # Initialize the store
        self._initialize_store()

    def _initialize_store(self):
        """Initialize or load the vector store"""
        index_path = os.path.join(self.vector_store_path, "index.faiss")

        if os.path.exists(index_path):
            print("Loading existing vector store...")
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✓ Vector store loaded successfully")
            except Exception as e:
                print(f"✗ Error loading vector store: {e}")
                print("Building new vector store...")
                self._build_vector_store()
        else:
            print("Building new vector store...")
            self._build_vector_store()

    def _build_vector_store(self):
        """Build vector store from HR documents"""
        loader = HRDocumentLoader(self.policies_path)
        documents = loader.load_documents()

        if not documents:
            raise ValueError("No documents found to index")

        print(f"Indexing {len(documents)} document chunks...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

        # Save the vector store
        os.makedirs(self.vector_store_path, exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)
        print("✓ Vector store saved successfully")

    def search(
        self,
        query: str,
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[Document]:
        """
        Search for relevant documents

        Args:
            query: Search query
            k: Number of results to return
            filter_type: Optional policy type filter

        Returns:
            List of relevant documents
        """
        if not self.vector_store:
            print("Warning: Vector store not initialized")
            return []

        try:
            if filter_type:
                # FAISS doesn't support native filtering, so we fetch more and filter
                results = self.vector_store.similarity_search(query, k=k * 3)
                filtered = [
                    doc for doc in results
                    if doc.metadata.get("policy_type") == filter_type
                ]
                return filtered[:k]
            else:
                return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def search_with_scores(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """Search with relevance scores"""
        if not self.vector_store:
            return []

        try:
            return self.vector_store.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def add_documents(self, documents: List[Document]):
        """Add new documents to the vector store"""
        if not self.vector_store:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)

        # Save updated store
        self.vector_store.save_local(self.vector_store_path)
        print(f"✓ Added {len(documents)} documents to vector store")

    def refresh_index(self):
        """Rebuild the vector store from scratch"""
        print("Refreshing vector store...")
        self._build_vector_store()

    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """Get a retriever for use with LangChain chains"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        return self.vector_store.as_retriever(
            search_kwargs=search_kwargs or {"k": 5}
        )
