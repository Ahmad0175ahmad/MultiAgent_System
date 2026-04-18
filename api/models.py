from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    llm_provider: Optional[str] = None
    output_format: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    session_id: str
    status: str


class TaskStatusResponse(BaseModel):
    status: str
    progress: float
    current_agent: Optional[str]
    logs: List[str]


class TaskResultResponse(BaseModel):
    output: Optional[str]
    agent_trace: Optional[Dict[str, Any]]
    sources: Optional[List[str]]
    created_at: Optional[str]


class DocumentUploadResponse(BaseModel):
    doc_id: str
    chunks_stored: int
    status: str


class MemorySearchResult(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]


class MemorySearchResponse(BaseModel):
    results: List[MemorySearchResult]


class SessionSummaryResponse(BaseModel):
    session_id: str
    goal: str
    status: str
    created_at: str
