from template_bot import storage


def test_set_and_get_roundtrip() -> None:
    storage.set(123, "welcome_channel_id", 456)

    assert storage.get(123, "welcome_channel_id") == 456


def test_get_missing_key_returns_default() -> None:
    assert storage.get(123, "missing", "fallback") == "fallback"


def test_values_are_isolated_per_guild() -> None:
    storage.set(1, "auto_role_id", 111)
    storage.set(2, "auto_role_id", 222)

    assert storage.get(1, "auto_role_id") == 111
    assert storage.get(2, "auto_role_id") == 222


def test_all_for_guild() -> None:
    storage.set(1, "a", 1)
    storage.set(1, "b", 2)

    assert storage.all_for_guild(1) == {"a": 1, "b": 2}
    assert storage.all_for_guild(999) == {}
