from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.rag_system.service import RAGService


if __name__ == "__main__":
    result = RAGService().ingest_default_documents()
    print(result)
