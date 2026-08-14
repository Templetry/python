"""CRUD endpoints for TemplateEntity.

Mounted automatically: main.py walks the routers package, so this piece
wires itself without touching any existing file (ADR-0014).
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from template_app.deps import CurrentUser, SessionDep
from template_app.models_template_entity import (
    TemplateEntity,
    TemplateEntityCreate,
    TemplateEntityRead,
    TemplateEntityUpdate,
)

router = APIRouter(prefix="/template-entity", tags=["template-entity"])


@router.post("", response_model=TemplateEntityRead, status_code=status.HTTP_201_CREATED)
def create(payload: TemplateEntityCreate, session: SessionDep, _: CurrentUser) -> TemplateEntity:
    row = TemplateEntity(**payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.get("", response_model=list[TemplateEntityRead])
def list_all(session: SessionDep, _: CurrentUser, limit: int = 50, offset: int = 0) -> list[TemplateEntity]:
    return list(session.exec(select(TemplateEntity).offset(offset).limit(limit)).all())


@router.get("/{row_id}", response_model=TemplateEntityRead)
def read_one(row_id: int, session: SessionDep, _: CurrentUser) -> TemplateEntity:
    row = session.get(TemplateEntity, row_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    return row


@router.patch("/{row_id}", response_model=TemplateEntityRead)
def update(row_id: int, payload: TemplateEntityUpdate, session: SessionDep, _: CurrentUser) -> TemplateEntity:
    row = session.get(TemplateEntity, row_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete("/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(row_id: int, session: SessionDep, _: CurrentUser) -> None:
    row = session.get(TemplateEntity, row_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    session.delete(row)
    session.commit()
