from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class ChatReactionConfig:
    chat_id: str
    user_id: str
    enabled: bool = False
    map: Dict[str, str] = field(default_factory=dict)


class JsonConfigStore:
    """Small JSON store for per-chat reaction command mappings."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8") or "{}")

    def _write_all(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)

    @staticmethod
    def _key(chat_id: str, user_id: str) -> str:
        return f"{chat_id}:{user_id}"

    def save(self, config: ChatReactionConfig) -> None:
        data = self._read_all()
        data[self._key(config.chat_id, config.user_id)] = asdict(config)
        self._write_all(data)

    def load(self, chat_id: str, user_id: str) -> ChatReactionConfig | None:
        raw = self._read_all().get(self._key(chat_id, user_id))
        if not raw:
            return None
        return ChatReactionConfig(
            chat_id=str(raw.get("chat_id", chat_id)),
            user_id=str(raw.get("user_id", user_id)),
            enabled=bool(raw.get("enabled", False)),
            map={str(k): str(v) for k, v in (raw.get("map") or {}).items()},
        )

    def delete(self, chat_id: str, user_id: str) -> bool:
        data = self._read_all()
        removed = data.pop(self._key(chat_id, user_id), None) is not None
        if removed:
            self._write_all(data)
        return removed
