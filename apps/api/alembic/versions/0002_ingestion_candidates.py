"""ingestion pages and question candidates

Revision ID: 0002_ingestion_candidates
Revises: 0001_initial
Create Date: 2026-06-07 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_ingestion_candidates"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("document_id", "page", name="uq_document_pages_document_page"),
    )
    op.create_index("ix_document_pages_document_id", "document_pages", ["document_id"])

    op.create_table(
        "question_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=True),
        sa.Column("option_a", sa.Text(), nullable=True),
        sa.Column("option_b", sa.Text(), nullable=True),
        sa.Column("option_c", sa.Text(), nullable=True),
        sa.Column("option_d", sa.Text(), nullable=True),
        sa.Column("correct_answer", sa.String(length=1), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("area", sa.String(length=80), nullable=True),
        sa.Column("subarea", sa.String(length=120), nullable=True),
        sa.Column("topic", sa.String(length=160), nullable=True),
        sa.Column("subtopic", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_question_candidates_document_id", "question_candidates", ["document_id"])
    op.create_index("ix_question_candidates_area", "question_candidates", ["area"])
    op.create_index("ix_question_candidates_topic", "question_candidates", ["topic"])
    op.create_index("ix_question_candidates_status", "question_candidates", ["status"])


def downgrade() -> None:
    op.drop_table("question_candidates")
    op.drop_table("document_pages")
