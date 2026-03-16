from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import HashingVectorizer

from rag_system.chunker import TextChunk

try:
    import chromadb
except ImportError:  # pragma: no cover - optional in current environment
    chromadb = None


@dataclass
class RetrievalResult:
    chunk: TextChunk
    score: float

    def to_source_dict(self) -> dict[str, str]:
        payload = self.chunk.to_source_dict()
        payload["score"] = f"{self.score:.4f}"
        return payload


class HashEmbeddingFunction:
    def __init__(self, dimensions: int) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=dimensions,
            alternate_sign=False,
            norm="l2",
        )

    def __call__(self, texts: list[str]) -> list[list[float]]:
        matrix = self.vectorizer.transform(texts)
        return matrix.astype("float32").toarray().tolist()


class InMemoryCollection:
    def __init__(self, embedding_function: HashEmbeddingFunction) -> None:
        self.embedding_function = embedding_function
        self.documents: list[str] = []
        self.ids: list[str] = []
        self.metadatas: list[dict[str, str]] = []
        self.embeddings: list[list[float]] = []

    def upsert(self, ids: list[str], documents: list[str], metadatas: list[dict[str, str]]) -> None:
        self.documents = list(documents)
        self.ids = list(ids)
        self.metadatas = list(metadatas)
        self.embeddings = self.embedding_function(documents)

    def query(self, query_texts: list[str], n_results: int) -> dict[str, list[list[object]]]:
        if not self.documents:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        query_embedding = self.embedding_function(query_texts)[0]
        scored = []
        for idx, embedding in enumerate(self.embeddings):
            score = sum((a - b) ** 2 for a, b in zip(query_embedding, embedding, strict=False))
            scored.append((score, idx))
        scored.sort(key=lambda item: item[0])
        selected = scored[:n_results]
        return {
            "ids": [[self.ids[idx] for _, idx in selected]],
            "documents": [[self.documents[idx] for _, idx in selected]],
            "metadatas": [[self.metadatas[idx] for _, idx in selected]],
            "distances": [[score for score, _ in selected]],
        }


class ChromaVectorStore:
    def __init__(self, persist_dir: Path, dimensions: int, collection_name: str = "industrial_docs") -> None:
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_function = HashEmbeddingFunction(dimensions)
        self.collection_name = collection_name
        if chromadb is not None:
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
        else:
            self.collection = InMemoryCollection(self.embedding_function)

    def rebuild(self, chunks: list[TextChunk]) -> None:
        if chromadb is not None:
            existing = self.collection.get()
            ids = existing.get("ids", [])
            if ids:
                self.collection.delete(ids=ids)
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {"source": chunk.source, **chunk.metadata}
                for chunk in chunks
            ],
        )

    def search(self, query: str, top_k: int) -> list[RetrievalResult]:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        payload: list[RetrievalResult] = []
        for chunk_id, document, metadata, distance in zip(ids, docs, metadatas, distances, strict=False):
            source = metadata.get("source", "unknown")
            chunk_metadata = {key: str(value) for key, value in metadata.items() if key != "source"}
            payload.append(
                RetrievalResult(
                    chunk=TextChunk(chunk_id=str(chunk_id), source=source, text=str(document), metadata=chunk_metadata),
                    score=float(distance),
                )
            )
        return payload
