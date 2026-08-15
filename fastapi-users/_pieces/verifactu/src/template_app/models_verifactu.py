"""Verifactu record models for TemplateApp (Spain, RD 1007/2023).

A *registro de facturación* is append-only: once written it is never
updated or deleted, because its fingerprint is chained into the next one.
Corrections are expressed by adding an `anulacion` record, never by
editing the original.
"""

from datetime import datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


class RecordKind(StrEnum):
    ALTA = "alta"
    ANULACION = "anulacion"


class InvoiceRecord(SQLModel, table=True):
    """One invoicing record of the chain."""

    __tablename__ = "verifactu_record"

    id: int | None = Field(default=None, primary_key=True)
    kind: str = Field(default=RecordKind.ALTA, index=True)

    # Identification of the invoice (the fields the fingerprint covers).
    id_emisor_factura: str = Field(index=True)      # issuer NIF
    num_serie_factura: str = Field(index=True)      # series + number
    fecha_expedicion: str                           # dd-mm-yyyy, as the spec writes it
    tipo_factura: str = "F1"                        # F1, F2, R1…
    cuota_total: str = "0"                          # tax amount, decimal as text
    importe_total: str = "0"                        # invoice total, decimal as text

    # Chain.
    huella: str = Field(index=True)                 # this record's SHA-256, uppercase hex
    huella_anterior: str = ""                       # previous record's fingerprint
    fecha_hora_huso_gen_registro: str = ""          # ISO 8601 with offset

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventRecord(SQLModel, table=True):
    """Software event log required of an invoicing system."""

    __tablename__ = "verifactu_event"

    id: int | None = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    event: str = Field(index=True)   # startup | shutdown | export | anomaly | …
    detail: str = ""
    actor: str = ""


class InvoiceRecordRead(SQLModel):
    id: int
    kind: str
    id_emisor_factura: str
    num_serie_factura: str
    fecha_expedicion: str
    tipo_factura: str
    cuota_total: str
    importe_total: str
    huella: str
    huella_anterior: str
    fecha_hora_huso_gen_registro: str


class EventRecordRead(SQLModel):
    id: int
    at: datetime
    event: str
    detail: str
    actor: str
