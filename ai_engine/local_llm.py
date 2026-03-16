from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.config import MODEL_FILE

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover - optional dependency in this environment
    Llama = None  # type: ignore[assignment]


@dataclass
class LocalLLMRuntime:
    model_path: str = MODEL_FILE
    n_ctx: int = 4096
    n_threads: int = 4

    def __post_init__(self) -> None:
        self._llm = None
        if Llama is not None and Path(self.model_path).exists():
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False,
            )

    @property
    def model_name(self) -> str:
        return Path(self.model_path).name

    def generate(self, prompt: str) -> str:
        if self._llm is None:
            return self._fallback_response(prompt)

        result = self._llm.create_completion(
            prompt=prompt,
            max_tokens=700,
            temperature=0.2,
            top_p=0.9,
            stop=["<|endoftext|>"],
        )
        return result["choices"][0]["text"].strip()

    def health(self) -> dict[str, str]:
        return {
            "status": "online" if self._llm is not None else "degraded",
            "model": self.model_name,
            "model_found": str(Path(self.model_path).exists()).lower(),
        }

    def _fallback_response(self, prompt: str) -> str:
        return (
            "Embedded model runtime is not active. The assistant is running in degraded advisory mode.\n\n"
            "Use the machine-state checks and retrieved evidence below for manual troubleshooting.\n\n"
            f"Prompt digest:\n{prompt[:1200]}"
        )
