"""
LlamaIndex Service for Product Knowledge Retrieval
Manages vector index, embeddings, and semantic search
"""

import os
import requests
from typing import List, Dict, Optional
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.embeddings import BaseEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from .document_loaders import MasterDocumentLoader


class OllamaEmbedding(BaseEmbedding):
    """
    Custom embedding class that uses local Ollama API for embeddings.
    This allows us to use free, local embeddings instead of OpenAI.
    """

    model_name: str = "nomic-embed-text"
    _base_url: str = "http://host.docker.internal:11434"
    _embed_dim: int = 768  # nomic-embed-text dimension

    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        base_url: str = "http://host.docker.internal:11434",
        **kwargs
    ):
        super().__init__(model_name=model_name, **kwargs)
        self._base_url = base_url

    @classmethod
    def class_name(cls) -> str:
        return "OllamaEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query."""
        return self._get_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text."""
        return self._get_embedding(text)

    def _get_embedding(self, text: str) -> List[float]:
        """Call Ollama API to get embedding."""
        try:
            response = requests.post(
                f"{self._base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
        except Exception as e:
            print(f"⚠️ Ollama embedding failed: {str(e)[:100]}")
            # Return zero vector as fallback
            return [0.0] * self._embed_dim

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async version - falls back to sync for now."""
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async version - falls back to sync for now."""
        return self._get_text_embedding(text)


class IndexService:
    """
    Manages LlamaIndex for product knowledge retrieval.
    No hardcoded knowledge - everything is loaded dynamically from Django models!
    """

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.index = None
        self.query_engine = None
        self.retriever = None
        self._settings_initialized = False

        # Auto-load existing index if it exists
        if os.path.exists(persist_dir):
            try:
                self._load_existing_index()
            except Exception as e:
                print(f"Warning: Could not load existing index: {e}")
                print("Index will need to be built before use")

    def _initialize_settings(self):
        """Configure LlamaIndex global settings (lazy initialization)"""
        if self._settings_initialized:
            return

        # Use Ollama for embeddings (free, local, working!)
        print("🔧 Using Ollama for embeddings (host.docker.internal:11434)")
        Settings.embed_model = OllamaEmbedding(
            model_name="nomic-embed-text",
            base_url="http://host.docker.internal:11434"
        )

        # Use Claude for LLM (for RAG query engine)
        claude_api_key = os.getenv('CLAUDE_API_KEY')
        if claude_api_key:
            print("🔧 Using Claude Sonnet 4 for LLM (RAG query engine)")
            Settings.llm = Anthropic(
                model="claude-sonnet-4-20250514",
                api_key=claude_api_key,
                temperature=0.7,
                max_tokens=4096
            )
        else:
            print("⚠️ CLAUDE_API_KEY not set - LLM features disabled")

        # Set chunk size for text splitting
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50

        self._settings_initialized = True

    def _load_existing_index(self):
        """Load existing index from disk"""
        # Initialize settings first
        self._initialize_settings()

        print(f"Loading existing index from {self.persist_dir}...")

        # Initialize ChromaDB vector store
        chroma_client = chromadb.PersistentClient(path=self.persist_dir)

        # Get existing collection
        try:
            collection = chroma_client.get_collection(
                name="marcus_ecommerce_knowledge"
            )
        except Exception:
            # Collection doesn't exist
            return

        # Create vector store from existing collection
        vector_store = ChromaVectorStore(chroma_collection=collection)

        # Load index from vector store
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store
        )

        # Create retriever and query engine
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=5
        )

        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever
        )

        print(f"✓ Loaded existing index from {self.persist_dir}")

    def build_index(self, persist_dir: str = None):
        """
        Build or load the vector index from Django models.
        This should be called on startup or when data changes.
        """
        # Use instance persist_dir if not provided
        if persist_dir is None:
            persist_dir = self.persist_dir

        # Initialize settings on first use
        self._initialize_settings()

        print("Building LlamaIndex from Django models...")

        # Load all documents from Django database
        documents = MasterDocumentLoader.load_all()

        if not documents:
            print("Warning: No documents loaded!")
            return

        # Initialize ChromaDB vector store
        chroma_client = chromadb.PersistentClient(path=persist_dir)

        # Create or get collection
        collection = chroma_client.get_or_create_collection(
            name="marcus_ecommerce_knowledge"
        )

        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Build index from documents
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )

        # Create retriever (top 5 most relevant documents)
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=5
        )

        # Create query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever
        )

        print(f"✓ Index built successfully with {len(documents)} documents")

    def rebuild_index(self, persist_dir: str = None):
        """
        Completely rebuild the index (useful when database changes significantly)
        Deletes the entire collection and rebuilds from scratch to avoid duplicates.
        """
        # Use instance persist_dir if not provided
        if persist_dir is None:
            persist_dir = self.persist_dir

        # Initialize settings first
        self._initialize_settings()

        # Delete the collection in ChromaDB instead of deleting files
        try:
            chroma_client = chromadb.PersistentClient(path=persist_dir)
            chroma_client.delete_collection(name="marcus_ecommerce_knowledge")
            print(f"✓ Deleted old collection from ChromaDB")
        except Exception as e:
            print(f"Note: Could not delete collection (may not exist): {e}")

        # Build fresh index
        self.build_index(persist_dir)

    def query(self, query_text: str, top_k: int = 5) -> Dict:
        """
        Query the index for relevant information.
        Returns retrieved documents and their relevance scores.
        """
        if not self.retriever:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Retrieve relevant documents
        retrieved_nodes = self.retriever.retrieve(query_text)

        # Format results
        results = {
            "query": query_text,
            "documents": []
        }

        for node in retrieved_nodes[:top_k]:
            results["documents"].append({
                "text": node.text,
                "score": node.score,
                "metadata": node.metadata
            })

        return results

    def search_products(self, query: str, category_id: Optional[int] = None) -> List[Dict]:
        """
        Search for products based on natural language query.
        Returns list of matching products with scores.
        """
        if not self.retriever:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Retrieve relevant documents
        retrieved_nodes = self.retriever.retrieve(query)

        # Filter for product documents
        products = []
        for node in retrieved_nodes:
            metadata = node.metadata
            if metadata.get("type") == "product":
                # Filter by category if specified
                if category_id and metadata.get("category_id") != category_id:
                    continue

                products.append({
                    "id": metadata.get("product_id"),
                    "name": metadata.get("product_name"),
                    "category": metadata.get("category_name"),
                    "base_price": metadata.get("base_price"),
                    "relevance_score": node.score,
                    "text": node.text
                })

        return products

    def search_categories(self, query: str) -> List[Dict]:
        """
        Search for categories based on natural language query.
        """
        if not self.retriever:
            raise RuntimeError("Index not built. Call build_index() first.")

        retrieved_nodes = self.retriever.retrieve(query)

        categories = []
        seen_categories = set()

        for node in retrieved_nodes:
            metadata = node.metadata
            if metadata.get("type") == "category":
                category_id = metadata.get("category_id")
                if category_id not in seen_categories:
                    categories.append({
                        "id": category_id,
                        "name": metadata.get("category_name"),
                        "parts_count": metadata.get("parts_count"),
                        "relevance_score": node.score
                    })
                    seen_categories.add(category_id)

        return categories

    def get_part_options(self, query: str, category_name: Optional[str] = None) -> List[Dict]:
        """
        Search for part options based on query.
        Useful for answering questions like "What wheel options are available?"
        """
        if not self.retriever:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Enhance query with category context
        if category_name:
            enhanced_query = f"{query} for {category_name}"
        else:
            enhanced_query = query

        retrieved_nodes = self.retriever.retrieve(enhanced_query)

        parts = []
        for node in retrieved_nodes:
            metadata = node.metadata
            if metadata.get("type") == "part":
                parts.append({
                    "part_name": metadata.get("part_name"),
                    "category": metadata.get("category_name"),
                    "step": metadata.get("step"),
                    "options_count": metadata.get("options_count"),
                    "relevance_score": node.score,
                    "description": node.text
                })

        return parts

    def get_compatibility_info(self, query: str) -> List[Dict]:
        """
        Search for compatibility rules based on query.
        """
        if not self.retriever:
            raise RuntimeError("Index not built. Call build_index() first.")

        retrieved_nodes = self.retriever.retrieve(query)

        rules = []
        for node in retrieved_nodes:
            metadata = node.metadata
            if metadata.get("type") in ["incompatibility_rule", "price_adjustment_rule"]:
                rules.append({
                    "type": metadata.get("type"),
                    "description": node.text,
                    "relevance_score": node.score,
                    "metadata": metadata
                })

        return rules

    def ask_question(self, question: str) -> str:
        """
        Ask a natural language question and get an answer.
        Uses the query engine to synthesize an answer from retrieved context.
        """
        if not self.query_engine:
            raise RuntimeError("Index not built. Call build_index() first.")

        response = self.query_engine.query(question)
        return str(response)

    def get_stats(self) -> Dict:
        """
        Get statistics about the indexed knowledge base.
        """
        if not self.index:
            return {"status": "Index not built"}

        # Get document counts by type
        # This would require iterating through all documents
        # For now, return basic info
        return {
            "status": "Index ready",
            "index_type": "VectorStoreIndex",
            "vector_store": "ChromaDB",
            "embedding_model": "nomic-embed-text (Ollama)",
            "embedding_cost": "FREE (local)"
        }


# Global instance (singleton pattern)
_index_service_instance = None


def get_index_service() -> IndexService:
    """
    Get or create the global IndexService instance.
    This ensures we only load the index once per application lifecycle.
    """
    global _index_service_instance

    if _index_service_instance is None:
        _index_service_instance = IndexService()

    return _index_service_instance
