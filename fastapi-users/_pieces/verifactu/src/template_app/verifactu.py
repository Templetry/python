"""Verifactu fingerprint, chain and QR payload (Spain, RD 1007/2023).

Scope, stated plainly:

* This module implements the **mechanism** — record shape, SHA-256
  fingerprint, chaining, verification, QR payload, event log.
* It does **not** submit anything to the AEAT and does **not** hardcode
  any AEAT URL. Submission needs a qualified certificate and the endpoint
  published in the AEAT technical document; wire it through `Submitter`.
* It covers Verifactu mode only. Non-Verifactu mode additionally requires
  qualified electronic signatures and software self-protection.

The fingerprint template below is the one AEAT documents in *"Detalle de
las especificaciones técnicas para la generación de la huella o hash de
los registros"*. `EXAMPLE_ALTA_STRING` reproduces the published worked
example and is asserted in the tests — check it against the official PDF
when you adopt this piece, then keep the test as your regression net.
"""

import hashlib
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from typing import Protocol
from urllib.parse import urlencode

from sqlmodel import Session, select

from template_app.models_verifactu import EventRecord, InvoiceRecord, RecordKind

# NIF of the obligated issuer.
ISSUER_NIF = "unset"  # tpl:var issuer_nif unset

# AEAT verification URL embedded in the QR. Unset until you take it from
# the AEAT technical document — a wrong URL fails silently at inspection
# time, so this piece refuses to guess one.
QR_BASE_URL = "unset"  # tpl:var qr_base_url unset

# Sentinel meaning "the operator has not configured this yet".
UNSET = "unset"

# Field order of an "alta" record fingerprint, per the specification.
ALTA_FIELDS: Sequence[str] = (
    "IDEmisorFactura",
    "NumSerieFactura",
    "FechaExpedicionFactura",
    "TipoFactura",
    "CuotaTotal",
    "ImporteTotal",
    "Huella",
    "FechaHoraHusoGenRegistro",
)

# The worked example published with the specification.
EXAMPLE_ALTA_STRING = (
    "IDEmisorFactura=89890001K&NumSerieFactura=12345678/G33"
    "&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35"
    "&ImporteTotal=123.45&Huella=&FechaHoraHusoGenRegistro=2024-01-01T19:20:30+01:00"
)


def normalize(value: object) -> str:
    """Spec rules: strip spaces; trailing decimal zeros are irrelevant."""
    text = str(value if value is not None else "").replace(" ", "")
    if "." in text:
        head, _, tail = text.partition(".")
        tail = tail.rstrip("0")
        text = f"{head}.{tail}" if tail else head
    return text


def fingerprint_string(values: dict[str, object], fields: Sequence[str] = ALTA_FIELDS) -> str:
    """Build the exact string the fingerprint is computed over.

    Missing values render as the bare `name=`, which is how the chain's
    first record carries an empty `Huella`.
    """
    return "&".join(f"{name}={normalize(values.get(name, ''))}" for name in fields)


def fingerprint(values: dict[str, object], fields: Sequence[str] = ALTA_FIELDS) -> str:
    """SHA-256 of the assembled string, uppercase hex (64 chars)."""
    return hashlib.sha256(fingerprint_string(values, fields).encode("utf-8")).hexdigest().upper()


def last_record(session: Session) -> InvoiceRecord | None:
    return session.exec(select(InvoiceRecord).order_by(InvoiceRecord.id.desc())).first()


def register_invoice(
    session: Session,
    *,
    num_serie: str,
    fecha_expedicion: str,
    importe_total: object,
    cuota_total: object = "0",
    tipo_factura: str = "F1",
    kind: RecordKind = RecordKind.ALTA,
    issuer_nif: str | None = None,
    generated_at: datetime | None = None,
) -> InvoiceRecord:
    """Append one record, chained to the previous one.

    `fecha_expedicion` is written as the spec writes it (dd-mm-yyyy).
    """
    previous = last_record(session)
    stamp = (generated_at or datetime.now(timezone.utc).astimezone()).isoformat(timespec="seconds")
    values = {
        "IDEmisorFactura": issuer_nif or ISSUER_NIF,
        "NumSerieFactura": num_serie,
        "FechaExpedicionFactura": fecha_expedicion,
        "TipoFactura": tipo_factura,
        "CuotaTotal": cuota_total,
        "ImporteTotal": importe_total,
        "Huella": previous.huella if previous else "",
        "FechaHoraHusoGenRegistro": stamp,
    }
    record = InvoiceRecord(
        kind=kind,
        id_emisor_factura=str(values["IDEmisorFactura"]),
        num_serie_factura=num_serie,
        fecha_expedicion=fecha_expedicion,
        tipo_factura=tipo_factura,
        cuota_total=normalize(cuota_total),
        importe_total=normalize(importe_total),
        huella=fingerprint(values),
        huella_anterior=previous.huella if previous else "",
        fecha_hora_huso_gen_registro=stamp,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def verify_chain(session: Session) -> list[int]:
    """Re-compute every fingerprint. Returns the ids that no longer match.

    An empty list is the only acceptable result: anything else means a
    record was altered after the fact, which is exactly what the chain
    exists to expose.
    """
    broken: list[int] = []
    previous_hash = ""
    for record in session.exec(select(InvoiceRecord).order_by(InvoiceRecord.id)).all():
        expected = fingerprint(
            {
                "IDEmisorFactura": record.id_emisor_factura,
                "NumSerieFactura": record.num_serie_factura,
                "FechaExpedicionFactura": record.fecha_expedicion,
                "TipoFactura": record.tipo_factura,
                "CuotaTotal": record.cuota_total,
                "ImporteTotal": record.importe_total,
                "Huella": previous_hash,
                "FechaHoraHusoGenRegistro": record.fecha_hora_huso_gen_registro,
            }
        )
        if expected != record.huella or record.huella_anterior != previous_hash:
            broken.append(record.id)
        previous_hash = record.huella
    return broken


def qr_payload(record: InvoiceRecord, base_url: str | None = None) -> str:
    """The string a Verifactu QR encodes: the AEAT verification URL with
    issuer NIF, invoice number, date and total.

    Raises when no base URL is configured, rather than emitting a QR that
    would not validate.
    """
    url = base_url if base_url is not None else QR_BASE_URL
    if not url or url == UNSET:
        raise ValueError(
            "qr_base_url is not set: take the verification URL from the AEAT "
            "technical document and configure it before printing QR codes"
        )
    query = urlencode(
        {
            "nif": record.id_emisor_factura,
            "numserie": record.num_serie_factura,
            "fecha": record.fecha_expedicion,
            "importe": record.importe_total,
        }
    )
    return f"{url}?{query}"


def log_event(session: Session, event: str, detail: str = "", actor: str = "") -> EventRecord:
    """Append to the software event log the regulation requires."""
    row = EventRecord(event=event, detail=detail, actor=actor)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


class Submitter(Protocol):
    """Transport to the AEAT. Implement with your qualified certificate."""

    def submit(self, records: Iterable[InvoiceRecord]) -> None: ...


class NullSubmitter:
    """Default: records are chained and stored, nothing is transmitted.

    Replace this before operating in Verifactu mode — storing records is
    only half of the obligation.
    """

    def submit(self, records: Iterable[InvoiceRecord]) -> None:
        return None
