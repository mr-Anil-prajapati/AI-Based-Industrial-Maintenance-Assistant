from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

from backend.config import EMBEDDING_DIMENSIONS
from backend.rag_system.chunker import TextChunk


@dataclass
class RetrievalResult:
    chunk: TextChunk
    score: float

    def to_source_dict(self) -> dict[str, str]:
        data = self.chunk.to_source_dict()
        data["score"] = f"{self.score:.4f}"
        return data


class VectorStore:
    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = HashingVectorizer(
            n_features=EMBEDDING_DIMENSIONS,
            alternate_sign=False,
            norm="l2",
        )
        self.index_path = self.persist_dir / "faiss.index"
        self.meta_path = self.persist_dir / "chunks.pkl"
        self.index: faiss.IndexFlatL2 | None = None
        self.chunks: list[TextChunk] = []
        self._load()

    def _load(self) -> None:
        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with self.meta_path.open("rb") as handle:
                self.chunks = pickle.load(handle)

    def rebuild(self, chunks: list[TextChunk]) -> None:
        if not chunks:
            self.index = None
            self.chunks = []
            return
        embeddings = self._embed([chunk.text for chunk in chunks])
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        self.chunks = list(chunks)
        faiss.write_index(self.index, str(self.index_path))
        with self.meta_path.open("wb") as handle:
            pickle.dump(self.chunks, handle)

    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        if self.index is None or not self.chunks:
            return []
        query_embedding = self._embed([query])
        distances, indices = self.index.search(query_embedding, top_k)
        results: list[RetrievalResult] = []
        for score, idx in zip(distances[0], indices[0], strict=False):
            if idx == -1:
                continue
            results.append(RetrievalResult(chunk=self.chunks[idx], score=float(score)))
        return results

    def _embed(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(texts)
        return matrix.astype("float32").toarray()
