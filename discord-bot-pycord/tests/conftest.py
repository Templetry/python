from pathlib import Path

import pytest

from template_bot import storage


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No test should read or write the real `data/guild_settings.json`."""
    monkeypatch.setattr(storage, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "_STORE_PATH", tmp_path / "guild_settings.json")
