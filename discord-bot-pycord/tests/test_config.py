import pytest

from template_bot.config import Settings


def test_from_env_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        Settings.from_env()


def test_from_env_reads_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")
    monkeypatch.setenv("BOT_PREFIX", "?")

    settings = Settings.from_env()

    assert settings.token == "fake-token"
    assert settings.prefix == "?"
