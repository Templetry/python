import pytest

from template_app.db import get_session
from template_app.main import app
from template_app.models_softdelete_demo import Document
from template_app.soft_delete import alive, deleted, get_alive, purge, restore, soft_delete


@pytest.fixture(name="session")
def session_fixture(client):
    generator = app.dependency_overrides[get_session]()
    session = next(generator)
    yield session
    generator.close()


def make(session, title: str) -> Document:
    doc = Document(title=title)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


def test_soft_delete_hides_without_destroying(client, session) -> None:
    keep, drop = make(session, "keep"), make(session, "drop")

    soft_delete(session, drop)

    assert [d.title for d in session.exec(alive(Document)).all()] == ["keep"]
    assert [d.title for d in session.exec(deleted(Document)).all()] == ["drop"]
    # The row is still there: history and foreign keys survive.
    assert session.get(Document, drop.id) is not None
    assert get_alive(session, Document, drop.id) is None
    assert get_alive(session, Document, keep.id) is not None


def test_delete_is_idempotent_and_restorable(client, session) -> None:
    doc = make(session, "doc")

    soft_delete(session, doc)
    first_stamp = doc.deleted_at
    soft_delete(session, doc)
    assert doc.deleted_at == first_stamp  # re-deleting keeps the original time

    restore(session, doc)
    assert doc.deleted_at is None
    assert [d.title for d in session.exec(alive(Document)).all()] == ["doc"]


def test_purge_removes_for_real(client, session) -> None:
    doc = make(session, "gone")
    purge(session, doc)
    assert session.get(Document, doc.id) is None
