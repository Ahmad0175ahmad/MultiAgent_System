"""
ChromaDB Memory Layer (M3)

Handles:
- Storing agent outputs
- Retrieving relevant context
- Managing collections

Author: AutoAgent
"""

from typing import List, Dict, Optional
import logging
import uuid
from datetime import datetime
import os

# Suppress transformers warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import chromadb
from chromadb.utils import embedding_functions

from config import settings


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MemoryManager:
    """
    Singleton Memory Manager for ChromaDB operations.
    """

    _instance = None

    COLLECTIONS = [
        "research_memory",
        "document_store",
        "task_outputs",
        "agent_scratchpad",
        "user_preferences",
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """Initialize ChromaDB client and embedding function"""
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH
            )

            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL,
                local_files_only=settings.EMBEDDING_LOCAL_FILES_ONLY,
            )

            # Ensure collections exist
            self.collections = {}
            for name in self.COLLECTIONS:
                self.collections[name] = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=self.embedding_fn
                )

            logger.info("ChromaDB initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    # -----------------------------------
    # STORE
    # -----------------------------------
    def store(
        self,
        collection_name: str,
        text: str,
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Store a document in a collection.

        Returns:
            doc_id (str)
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            doc_id = doc_id or str(uuid.uuid4())

            base_metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                "collection": collection_name,
            }

            if metadata:
                base_metadata.update(metadata)

            self.collections[collection_name].add(
                documents=[text],
                metadatas=[base_metadata],
                ids=[doc_id],
            )

            logger.info(f"Stored document in {collection_name} (id={doc_id})")
            return doc_id

        except Exception as e:
            logger.error(f"Store failed: {e}")
            raise

    # -----------------------------------
    # RETRIEVE
    # -----------------------------------
    def retrieve(
        self,
        collection_name: str,
        query: str,
        k: int = 5,
        threshold: float = 0.75,
    ) -> List[Dict]:
        """
        Retrieve top-k similar documents above threshold.

        Returns:
            List of {text, score, metadata}
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            results = self.collections[collection_name].query(
                query_texts=[query],
                n_results=k,
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            output = []

            for doc, meta, dist in zip(documents, metadatas, distances):
                # Convert distance → similarity score
                score = 1 - dist if dist is not None else 0

                if score >= threshold:
                    output.append({
                        "data": doc,
                        "score": score,
                        "metadata": meta,
                    })

            logger.info(f"Retrieved {len(output)} results from {collection_name}")
            return output

        except Exception as e:
            logger.error(f"Retrieve failed: {e}")
            return []

    # -----------------------------------
    # DELETE
    # -----------------------------------
    def delete(self, collection_name: str, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            self.collections[collection_name].delete(ids=[doc_id])
            logger.info(f"Deleted document {doc_id} from {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    # -----------------------------------
    # LIST COLLECTIONS
    # -----------------------------------
    def list_collections(self) -> List[str]:
        """Return available collection names"""
        try:
            return list(self.collections.keys())
        except Exception as e:
            logger.error(f"List collections failed: {e}")
            return []

    # -----------------------------------
    # CLEAR COLLECTION
    # -----------------------------------
    def clear_collection(self, collection_name: str) -> bool:
        """Delete all documents in a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            # Delete and recreate collection
            self.client.delete_collection(name=collection_name)

            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )

            logger.info(f"Cleared collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Clear collection failed: {e}")
            return False

    # -----------------------------------
    # QUERY (ChromaDB format)
    # -----------------------------------
    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5):
        """
        Query collection in ChromaDB format.
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            return self.collections[collection_name].query(
                query_texts=query_texts,
                n_results=n_results
            )
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    # -----------------------------------
    # ADD DOCUMENTS
    # -----------------------------------
    def add_documents(self, collection_name: str, documents: List[str], embeddings: List[List[float]], ids: List[str], metadatas: List[Dict]):
        """
        Add documents with embeddings to collection.
        """
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection: {collection_name}")

            self.collections[collection_name].add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to {collection_name}")
        except Exception as e:
            logger.error(f"Add documents failed: {e}")
            raise

    # -----------------------------------
    # SEARCH MEMORY (alias for retrieve)
    # -----------------------------------
    def search_memory(self, query: str, collection: str = "research_memory", k: int = 5):
        """
        Search memory (alias for retrieve).
        """
        return self.retrieve(collection, query, k)


# -----------------------------------
# SIMPLE TEST
# -----------------------------------
if __name__ == "__main__":
    memory = MemoryManager()

    print("\n--- TEST: STORE ---")
    doc_id = memory.store(
        collection_name="research_memory",
        text="Python is a powerful programming language.",
        metadata={"source": "test"}
    )
    print(f"Stored ID: {doc_id}")

    print("\n--- TEST: RETRIEVE ---")
    results = memory.retrieve(
        collection_name="research_memory",
        query="What is Python?",
        k=3
    )

    for r in results:
        print(r)

    print("\n--- TEST COMPLETE ---")
