from __future__ import annotations

from pathlib import Path

from ai_engine.local_llm import LocalLLMRuntime
from backend.config import (
    CHROMA_DB_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_DIMENSIONS,
    KNOWLEDGE_DIRS,
    TOP_K,
    UPLOADS_DIR,
)
from backend.machine_analysis.rules import MachineAnalyzer
from backend.plc_interface.protocols import get_read_only_client
from rag_system.chroma_store import ChromaVectorStore, RetrievalResult
from rag_system.chunker import TextChunk, split_text
from rag_system.document_loader import load_documents


SAFETY_NOTICE = (
    "Read-only advisory system. It never writes to PLCs, sends control commands, "
    "changes parameters, or modifies machine programs."
)


class AssistantService:
    def __init__(self) -> None:
        self.llm = LocalLLMRuntime()
        self.machine_analyzer = MachineAnalyzer()
        self.vector_store = ChromaVectorStore(CHROMA_DB_DIR, EMBEDDING_DIMENSIONS)

    def health(self) -> dict[str, str]:
        payload = {**self.llm.health(), "status": "ok"}
        payload["mode"] = "read-only"
        return payload

    def ingest_default_documents(self) -> dict[str, int]:
        docs = self._load_all_documents()
        chunks = self._build_chunks(docs)
        self.vector_store.rebuild(chunks)
        return {"documents_indexed": len(docs), "chunks_indexed": len(chunks)}

    def ingest_uploaded_documents(self, uploaded_files: list[Path]) -> dict[str, int]:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        imported_docs: list[tuple[Path, str]] = []
        for path in uploaded_files:
            target = UPLOADS_DIR / path.name
            if path.resolve() != target.resolve():
                target.write_bytes(path.read_bytes())
            imported_docs.extend([item for item in load_documents(UPLOADS_DIR) if item[0].resolve() == target.resolve()])

        all_docs = self._load_all_documents()
        all_chunks = self._build_chunks(all_docs)
        self.vector_store.rebuild(all_chunks)
        return {
            "documents_indexed": len(imported_docs),
            "chunks_indexed": len(self._build_chunks(imported_docs)),
        }

    def read_signals(self, protocol: str, asset_id: str) -> dict[str, object]:
        return get_read_only_client(protocol).read_signals(asset_id)

    def chat(self, question: str, asset_id: str, protocol: str) -> dict[str, object]:
        signals = self.read_signals(protocol, asset_id)
        machine_state = self.machine_analyzer.analyze(question, signals)
        retrieval = self.retrieve(question, asset_id)
        answer = self.generate_answer(question, asset_id, machine_state, retrieval)
        return {
            "answer": answer,
            "sources": [item.to_source_dict() for item in retrieval],
            "machine_state": machine_state,
            "safety_notice": SAFETY_NOTICE,
        }

    def retrieve(self, question: str, asset_id: str | None = None) -> list[RetrievalResult]:
        query = question if not asset_id else f"{question} {asset_id}"
        return self.vector_store.search(query, TOP_K)

    def generate_answer(
        self,
        question: str,
        asset_id: str,
        machine_state: dict[str, object],
        retrieved_chunks: list[RetrievalResult],
    ) -> str:
        context = "\n\n".join(
            f"Source: {item.chunk.source}\nEvidence: {item.chunk.text}" for item in retrieved_chunks
        ) or "No indexed maintenance documentation available."
        prompt = f"""
You are a senior industrial maintenance assistant running fully offline on Windows.
Safety rule: never suggest modifying PLC programs, sending PLC commands, changing machine parameters, or controlling machines.
Standards context: ISO 9001, ISO 12100, ISO 13849, IEC 61131-3, IEC 61508, IEC 62443.

Asset: {asset_id}
Question: {question}
Machine state analysis: {machine_state}

Retrieved documentation:
{context}

Respond with:
1. Explanation
2. Possible causes
3. Recommended checks
4. Read-only safety reminder
"""
        return self.llm.generate(prompt)

    def _load_all_documents(self) -> list[tuple[Path, str]]:
        docs: list[tuple[Path, str]] = []
        seen: set[Path] = set()
        for directory in KNOWLEDGE_DIRS + (UPLOADS_DIR,):
            if not directory.exists():
                continue
            for path, content in load_documents(directory):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    docs.append((path, content))
        return docs

    def _build_chunks(self, docs: list[tuple[Path, str]]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for path, content in docs:
            for idx, chunk_text in enumerate(split_text(content, CHUNK_SIZE, CHUNK_OVERLAP)):
                try:
                    source = str(path.relative_to(Path.cwd()))
                except ValueError:
                    source = str(path)
                chunks.append(
                    TextChunk(
                        chunk_id=f"{path.stem}-{idx}",
                        source=source,
                        text=chunk_text,
                        metadata={"document": path.name, "section": str(idx)},
                    )
                )
        return chunks
