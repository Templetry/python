"""A worked example of the mixin, and what the tests exercise.

Delete this module once your own models inherit `SoftDeleteMixin`.
"""

from sqlmodel import Field, SQLModel

from template_app.soft_delete import SoftDeleteMixin


class Document(SoftDeleteMixin, SQLModel, table=True):
    """Example entity: soft-deletable by inheriting the mixin."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
