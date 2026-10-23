"""add book tags table

Revision ID: 222630cd2eac
Revises: fdb3911eb56c
Create Date: 2026-07-02 15:30:48.774579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '222630cd2eac'
down_revision: Union[str, Sequence[str], None] = 'fdb3911eb56c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "book_tags",
        sa.Column("book_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.uid"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.uid"]),
        sa.PrimaryKeyConstraint("book_id", "tag_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("book_tags")
