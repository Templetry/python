"""Verifactu tests.

The first test is the important one: it pins the exact string the
fingerprint is computed over against the worked example published with
the AEAT specification. If that assertion ever fails, the records this
system produces are not compliant — which is the whole point of having it.
"""

import hashlib

import pytest

from template_app.db import get_session
from template_app.main import app
from template_app.models_verifactu import InvoiceRecord
from template_app.verifactu import (
    EXAMPLE_ALTA_STRING,
    fingerprint,
    fingerprint_string,
    log_event,
    normalize,
    qr_payload,
    register_invoice,
    verify_chain,
)


@pytest.fixture(name="session")
def session_fixture(client):
    generator = app.dependency_overrides[get_session]()
    session = next(generator)
    yield session
    generator.close()


def test_fingerprint_string_matches_the_published_example() -> None:
    values = {
        "IDEmisorFactura": "89890001K",
        "NumSerieFactura": "12345678/G33",
        "FechaExpedicionFactura": "01-01-2024",
        "TipoFactura": "F1",
        "CuotaTotal": "12.35",
        "ImporteTotal": "123.45",
        "Huella": "",
        "FechaHoraHusoGenRegistro": "2024-01-01T19:20:30+01:00",
    }
    assert fingerprint_string(values) == EXAMPLE_ALTA_STRING

    expected = hashlib.sha256(EXAMPLE_ALTA_STRING.encode("utf-8")).hexdigest().upper()
    digest = fingerprint(values)
    assert digest == expected
    assert len(digest) == 64 and digest == digest.upper()


def test_normalization_rules() -> None:
    assert normalize(" 12 34 ") == "1234"          # spaces removed
    assert normalize("123.10") == "123.1"          # trailing decimal zeros irrelevant
    assert normalize("123.00") == "123"
    assert normalize(None) == ""                    # absent renders as empty
    assert normalize(123.45) == "123.45"


def test_chain_links_each_record_to_the_previous(client, session) -> None:
    first = register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", cuota_total="21.00", issuer_nif="89890001K",
    )
    second = register_invoice(
        session, num_serie="A/2", fecha_expedicion="02-01-2026",
        importe_total="242.00", cuota_total="42.00", issuer_nif="89890001K",
    )

    assert first.huella_anterior == ""              # chain head
    assert second.huella_anterior == first.huella   # linked
    assert first.huella != second.huella
    assert verify_chain(session) == []


def test_tampering_breaks_the_chain(client, session) -> None:
    register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", issuer_nif="89890001K",
    )
    target = register_invoice(
        session, num_serie="A/2", fecha_expedicion="02-01-2026",
        importe_total="242.00", issuer_nif="89890001K",
    )
    register_invoice(
        session, num_serie="A/3", fecha_expedicion="03-01-2026",
        importe_total="363.00", issuer_nif="89890001K",
    )
    assert verify_chain(session) == []

    # Someone edits an amount after the fact — exactly what the chain exists
    # to expose. The edited record and every record after it stop verifying.
    target.importe_total = "1.00"
    session.add(target)
    session.commit()

    broken = verify_chain(session)
    assert target.id in broken


def test_qr_refuses_to_guess_the_aeat_url(client, session) -> None:
    record = register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", issuer_nif="89890001K",
    )
    with pytest.raises(ValueError, match="qr_base_url"):
        qr_payload(record)

    payload = qr_payload(record, base_url="https://example.test/ValidarQR")
    assert "nif=89890001K" in payload and "numserie=A%2F1" in payload
    assert "importe=121" in payload


def test_registry_endpoints_are_read_only(client, auth, session) -> None:
    register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", issuer_nif="89890001K",
    )
    log_event(session, "startup", "test run")

    assert client.get("/verifactu/records").status_code == 401

    records = client.get("/verifactu/records", headers=auth).json()
    assert len(records) == 1 and records[0]["num_serie_factura"] == "A/1"

    events = client.get("/verifactu/events", headers=auth).json()
    assert len(events) == 1 and events[0]["event"] == "startup"

    assert client.get("/verifactu/verify", headers=auth).json() == {"ok": True, "broken": []}

    # No write routes exist on the registry.
    assert client.post("/verifactu/records", json={}, headers=auth).status_code == 405
    assert client.delete("/verifactu/records", headers=auth).status_code == 405


def test_records_survive_as_evidence(client, session) -> None:
    """Corrections are new records, never edits of the old one."""
    from template_app.models_verifactu import RecordKind

    original = register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", issuer_nif="89890001K",
    )
    annul = register_invoice(
        session, num_serie="A/1", fecha_expedicion="01-01-2026",
        importe_total="121.00", issuer_nif="89890001K", kind=RecordKind.ANULACION,
    )
    assert annul.kind == "anulacion"
    assert session.get(InvoiceRecord, original.id) is not None
    assert verify_chain(session) == []
