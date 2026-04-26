"""add source_session_id to sessions

Revision ID: 0002_session_source_session_id
Revises: 0001_initial_schema
Create Date: 2026-04-26 00:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_session_source_session_id"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.add_column(
            sa.Column("source_session_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_sessions_source_session_id",
            "sessions",
            ["source_session_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index(
        "ix_sessions_source_session_id",
        "sessions",
        ["source_session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_source_session_id", table_name="sessions")
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.drop_constraint(
            "fk_sessions_source_session_id", type_="foreignkey"
        )
        batch_op.drop_column("source_session_id")
