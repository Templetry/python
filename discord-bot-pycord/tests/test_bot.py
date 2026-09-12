import pytest

from template_bot.config import Settings
from template_bot.main import build_bot


def test_build_bot_loads_extensions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")
    settings = Settings.from_env()

    bot = build_bot(settings)

    assert bot.settings is settings
    assert bot.cogs  # at least one cog was loaded
