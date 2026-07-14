import os
import logging

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class RAGVault:
    def __init__(self, db_path="C:\\Users\\vanga\\Documents\\Jarvis_Vault\\chroma_db"):
        self.db_path = db_path
        self.collection_name = "jarvis_memory"
        
        if CHROMA_AVAILABLE:
            self.client = chromadb.PersistentClient(path=self.db_path)
            # Use default sentence-transformers embedding function
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
        else:
            logging.warning("ChromaDB not found. Running RAGVault in Mock Mode.")
            self.client = None
            self.collection = None

    def embed_document(self, doc_id: str, text: str, metadata: dict = None):
        """Chunks and embeds text into the persistent vector database."""
        if metadata is None:
            metadata = {}
            
        if CHROMA_AVAILABLE:
            # Basic chunking simulation
            chunks = [text[i:i+500] for i in range(0, len(text), 500)]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [metadata for _ in chunks]
            
            self.collection.upsert(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Embedded document {doc_id} into {len(chunks)} chunks.")
        else:
            logging.info(f"[MOCK] Embedded document {doc_id} into vault.")

    def query_vault(self, user_query: str, n_results: int = 3):
        """Retrieves the top n most semantically similar chunks."""
        if CHROMA_AVAILABLE:
            results = self.collection.query(
                query_texts=[user_query],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        else:
            logging.info(f"[MOCK] Querying vault for: {user_query}")
            return [f"Mock result 1 for '{user_query}'", "Mock result 2", "Mock result 3"]
