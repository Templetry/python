"""Proves the profiles are wired, not decorative.

Each one is loaded and read back, so renaming a file or a key breaks here
rather than in whatever environment happened to depend on it.
"""

import pytest

from template_app.settings import get_settings


@pytest.fixture(autouse=True)
def _isolate_cache() -> None:
    # get_settings is cached, which is right for the app and wrong for a
    # suite that loads several profiles in one process.
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.parametrize("profile", ["development", "staging", "production"])
def test_each_profile_declares_its_own_name(profile: str) -> None:
    assert get_settings(profile).environment == profile


def test_development_keeps_detail_on_and_caching_off() -> None:
    settings = get_settings("development")
    assert settings.verbose_errors is True
    assert settings.cache_seconds == 0


def test_production_turns_detail_off_and_caches_longest() -> None:
    settings = get_settings("production")
    assert settings.verbose_errors is False
    assert settings.cache_seconds == 300


def test_staging_differs_from_both_neighbours() -> None:
    # Staging exists to be production-like while still debuggable, so it is
    # the one profile whose values must not equal either neighbour's.
    settings = get_settings("staging")
    assert settings.verbose_errors is True
    assert settings.cache_seconds == 30


def test_app_env_selects_the_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    assert get_settings().environment == "production"


def test_a_real_environment_variable_wins_over_the_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # This is the property that makes containers work: the platform sets real
    # variables and no profile file has to ship with the image.
    monkeypatch.setenv("CACHE_SECONDS", "7")
    assert get_settings("production").cache_seconds == 7


def test_the_cli_announces_the_profile_when_verbose(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The profile has to change behaviour somewhere, or it is decoration."""
    from typer.testing import CliRunner

    from template_app.cli import app

    monkeypatch.setenv("APP_ENV", "development")
    result = CliRunner().invoke(app, ["--name", "Python"])

    assert result.exit_code == 0
    assert "[development]" in result.output
    assert "Hello, Python!" in result.output


def test_production_stays_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    from typer.testing import CliRunner

    from template_app.cli import app

    monkeypatch.setenv("APP_ENV", "production")
    result = CliRunner().invoke(app, ["--name", "Python"])

    assert result.exit_code == 0
    assert "[production]" not in result.output
