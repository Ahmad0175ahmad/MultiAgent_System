"""
RAG Agent (Module M9)
Handles document ingestion and retrieval-augmented generation using ChromaDB.
"""

from typing import Optional, Dict, Any, List
import os
import uuid
import logging

# Suppress transformers warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from core.state import AgentState
from core.memory import MemoryManager
from core.llm_router import LLMRouter
from config import settings

from PyPDF2 import PdfReader


logger = logging.getLogger(__name__)


class RAGAgent:
    """Retrieval-Augmented Generation Agent"""

    def __init__(self):
        self.memory = MemoryManager()
        self.llm = LLMRouter()
        # ✅ SentenceTransformer hata diya — MemoryManager khud embed karta hai

    # -----------------------------
    # Document Ingestion
    # -----------------------------
    def ingest_document(self, file_path: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest a document (PDF or text) into ChromaDB.

        Args:
            file_path (str): Path to document
            collection_name (str, optional): Target collection

        Returns:
            dict: ingestion result
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            collection = collection_name or "document_store"
            doc_id = str(uuid.uuid4())

            # Read file
            text = self._read_file(file_path)

            # Split into chunks
            chunks = self._chunk_text(text)

            # ✅ memory.store() use karo — woh khud embed karega
            # Manual embeddings bilkul nahi — yahi conflict ka wajah tha
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_{i}"
                self.memory.store(
                    collection_name=collection,
                    text=chunk,
                    metadata={"doc_id": doc_id, "chunk_index": i},
                    doc_id=chunk_id
                )

            logger.info(f"Ingested {len(chunks)} chunks for doc {doc_id}")

            return {
                "doc_id": doc_id,
                "chunks_count": len(chunks),
                "collection_name": collection,
                "status": "success",
            }

        except Exception as e:
            logger.exception("Error ingesting document")
            return {
                "doc_id": None,
                "chunks_count": 0,
                "collection_name": collection_name,
                "status": "error",
                "error": str(e),
            }

    # -----------------------------
    # Run Agent (LangGraph ke liye)
    # -----------------------------
    def run(self, state: AgentState) -> AgentState:
        """
        Execute RAG pipeline for current task.

        Args:
            state (AgentState): shared state

        Returns:
            AgentState: updated state
        """
        try:
            task_id = state.get("current_task_id")
            if not task_id:
                raise ValueError("No current_task_id in state")

            task = next((t for t in state["tasks"] if t["id"] == task_id), None)
            if not task:
                raise ValueError(f"Task not found: {task_id}")

            question = task.get("description", "")

            result = self.answer_question(question)

            state["results"][task_id] = result
            return state

        except Exception as e:
            logger.exception("Error in RAGAgent.run")
            state["error_log"].append(str(e))
            return state

    # -----------------------------
    # Direct Question Answering
    # -----------------------------
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a direct question from the stored document context.

        Args:
            question (str): User's question

        Returns:
            dict: {answer, sources, confidence}
        """
        try:
            # ✅ retrieve() use karo — yeh bhi MemoryManager ka method hai
            results = self.memory.retrieve(
                collection_name="document_store",
                query=question,
                k=5,
                threshold=0.0,  # ✅ threshold 0 rakho — koi bhi result filter na ho
            )

            if not results:
                return {
                    "answer": "No relevant document context found.",
                    "sources": [],
                    "confidence": 0.0,
                }

            # Context banao retrieved chunks se
            context = "\n\n".join([r["data"] for r in results])
            chunk_ids = [r["metadata"].get("doc_id", "unknown") for r in results]

            prompt = (
                f"You are a helpful assistant. Answer the question based ONLY on the context below.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )

            answer = self.llm.generate(prompt)

            return {
                "answer": answer,
                "sources": chunk_ids,
                "confidence": round(min(1.0, len(results) / 5), 2),
            }

        except Exception as e:
            logger.exception("Error answering RAG question")
            return {
                "answer": f"RAG query failed: {e}",
                "sources": [],
                "confidence": 0.0,
            }

    # -----------------------------
    # Helpers
    # -----------------------------
    def _read_file(self, file_path: str) -> str:
        """Read PDF or text file and return plain text"""
        try:
            if file_path.lower().endswith(".pdf"):
                reader = PdfReader(file_path)
                pages_text = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                return "\n".join(pages_text)

            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            logger.exception("Error reading file")
            raise e

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping word-based chunks.

        Args:
            text (str): Full document text
            chunk_size (int): Words per chunk
            overlap (int): Overlapping words between chunks

        Returns:
            List[str]: list of text chunks
        """
        try:
            words = text.split()
            chunks = []

            start = 0
            while start < len(words):
                end = start + chunk_size
                chunk = " ".join(words[start:end])
                if chunk.strip():
                    chunks.append(chunk)
                start += chunk_size - overlap

            logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
            return chunks

        except Exception as e:
            logger.exception("Error chunking text")
            raise e