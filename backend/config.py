import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
APP_NAME = "Industrial AI Maintenance Assistant"
DATA_DIR = BASE_DIR / "data"
RAG_DATA_DIR = BASE_DIR / "rag_data"
KNOWLEDGE_DIRS = (DATA_DIR, RAG_DATA_DIR)
VECTOR_STORE_DIR = BASE_DIR / ".data" / "vector_store"
CHROMA_DB_DIR = BASE_DIR / "build" / "chroma_db"
STATIC_DIR = BASE_DIR / "frontend" / "web_dashboard"
CHAT_UI_DIR = BASE_DIR / "frontend" / "chat_ui"
UPLOADS_DIR = BASE_DIR / ".data" / "uploads"
MODEL_DIR = BASE_DIR / "models" / "deepseek-r1"
MODEL_FILE = os.getenv("LOCAL_MODEL_FILE", str(MODEL_DIR / "deepseek-r1-8b-q4.gguf"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
REST_GATEWAY_BASE_URL = os.getenv("REST_GATEWAY_BASE_URL", "http://localhost:9000")

EMBEDDING_DIMENSIONS = 512
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120
TOP_K = 4

READ_ONLY_PROTOCOLS = ("opcua", "modbus", "mqtt", "rest")
ALLOWED_DOCUMENT_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
