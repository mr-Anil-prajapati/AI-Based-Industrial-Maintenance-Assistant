from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    asset_id: str | None = None
    protocol: str = "opcua"


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]
    machine_state: dict[str, Any]
    safety_notice: str


class SignalSnapshot(BaseModel):
    asset_id: str
    protocol: str
    signals: dict[str, Any]


class IngestResponse(BaseModel):
    documents_indexed: int
    chunks_indexed: int


class ImportDocumentResponse(BaseModel):
    filenames: list[str]
    documents_indexed: int
    chunks_indexed: int
