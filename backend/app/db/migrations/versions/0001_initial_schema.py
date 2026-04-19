"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-19 00:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.String(length=128), nullable=False),
        sa.Column("params_json", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "created",
                "in_progress",
                "completed",
                "abandoned",
                name="session_status",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("seconds_per_problem", sa.Float(), nullable=True),
    )
    op.create_index("ix_sessions_lesson_id", "sessions", ["lesson_id"])

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(length=512), nullable=False),
        sa.Column("answer", sa.Float(), nullable=False),
        sa.Column("inputs_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["sessions.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "session_id", "ordinal", name="uq_problems_session_ordinal"
        ),
    )
    op.create_index("ix_problems_session_id", "problems", ["session_id"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("user_answer", sa.Float(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("elapsed_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problems.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "problem_id",
            "attempt_number",
            name="uq_attempts_problem_attempt_number",
        ),
    )
    op.create_index("ix_attempts_problem_id", "attempts", ["problem_id"])


def downgrade() -> None:
    op.drop_index("ix_attempts_problem_id", table_name="attempts")
    op.drop_table("attempts")
    op.drop_index("ix_problems_session_id", table_name="problems")
    op.drop_table("problems")
    op.drop_index("ix_sessions_lesson_id", table_name="sessions")
    op.drop_table("sessions")
