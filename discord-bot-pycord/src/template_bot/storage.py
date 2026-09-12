"""Tiny per-guild key/value store, backed by a JSON file on disk.

Discord bots almost always need *some* place to remember configuration or
state per server (a welcome channel, a mod-log channel, custom commands...)
without requiring a real database. This is that place. Cogs read and write
through `get`/`set`; nothing else should touch the file directly.
"""

import json
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_STORE_PATH = _DATA_DIR / "guild_settings.json"


def _load() -> dict[str, dict[str, Any]]:
    if not _STORE_PATH.exists():
        return {}
    return json.loads(_STORE_PATH.read_text(encoding="utf-8") or "{}")


def _save(data: dict[str, dict[str, Any]]) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get(guild_id: int, key: str, default: Any = None) -> Any:
    return _load().get(str(guild_id), {}).get(key, default)


def set(guild_id: int, key: str, value: Any) -> None:
    data = _load()
    data.setdefault(str(guild_id), {})[key] = value
    _save(data)


def all_for_guild(guild_id: int) -> dict[str, Any]:
    return _load().get(str(guild_id), {})
