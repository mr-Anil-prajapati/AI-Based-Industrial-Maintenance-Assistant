from __future__ import annotations

from abc import ABC, abstractmethod


class PLCWriteBlockedError(RuntimeError):
    """Raised when any write/control operation is attempted."""


class ReadOnlyPLCClient(ABC):
    protocol: str

    @abstractmethod
    def read_signals(self, asset_id: str) -> dict[str, object]:
        raise NotImplementedError

    def write_signal(self, *_args, **_kwargs) -> None:
        raise PLCWriteBlockedError(
            "Safety policy violation: the assistant is read-only and cannot write to PLCs or machine controls."
        )
