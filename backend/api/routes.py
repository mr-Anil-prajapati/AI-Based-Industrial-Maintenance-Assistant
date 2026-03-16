from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.schemas import (
    ChatRequest,
    ChatResponse,
    ImportDocumentResponse,
    IngestResponse,
    SignalSnapshot,
)
from backend.config import ALLOWED_DOCUMENT_EXTENSIONS, UPLOADS_DIR
from backend.assistant_service import AssistantService, SAFETY_NOTICE

router = APIRouter()

assistant_service = AssistantService()


@router.get("/health")
def health() -> dict[str, str]:
    return assistant_service.health()


@router.post("/ingest", response_model=IngestResponse)
def ingest_documents() -> IngestResponse:
    stats = assistant_service.ingest_default_documents()
    return IngestResponse(**stats)


@router.post("/ingest/upload", response_model=ImportDocumentResponse)
async def upload_documents(files: list[UploadFile] = File(...)) -> ImportDocumentResponse:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []
    for uploaded in files:
        suffix = Path(uploaded.filename).suffix.lower()
        if not uploaded.filename or suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}.",
            )
        target = UPLOADS_DIR / uploaded.filename
        target.write_bytes(await uploaded.read())
        saved_paths.append(target)

    stats = assistant_service.ingest_uploaded_documents(saved_paths)
    return ImportDocumentResponse(
        filenames=[path.name for path in saved_paths],
        documents_indexed=stats["documents_indexed"],
        chunks_indexed=stats["chunks_indexed"],
    )


@router.get("/signals/{protocol}/{asset_id}", response_model=SignalSnapshot)
def get_signals(protocol: str, asset_id: str) -> SignalSnapshot:
    return SignalSnapshot(
        asset_id=asset_id,
        protocol=protocol,
        signals=assistant_service.read_signals(protocol, asset_id),
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = assistant_service.chat(
            question=request.question,
            asset_id=request.asset_id or "motor-1",
            protocol=request.protocol,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ChatResponse(
        answer=str(result["answer"]),
        sources=list(result["sources"]),
        machine_state=dict(result["machine_state"]),
        safety_notice=str(result.get("safety_notice", SAFETY_NOTICE)),
    )
