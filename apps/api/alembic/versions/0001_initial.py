"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-06 00:00:00
"""
from __future__ import annotations

from alembic import op
from pgvector.sqlalchemy import Vector
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("area", sa.String(length=80), nullable=True),
        sa.Column("official_status", sa.String(length=80), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_id", sa.String(length=120), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("area", sa.String(length=80), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=True),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("option_a", sa.Text(), nullable=False),
        sa.Column("option_b", sa.Text(), nullable=False),
        sa.Column("option_c", sa.Text(), nullable=False),
        sa.Column("option_d", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("is_invalid", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_incomplete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_questions_area", "questions", ["area"])
    op.create_index("ix_questions_external_id", "questions", ["external_id"], unique=False)
    op.create_index("ix_questions_year", "questions", ["year"])

    op.create_table(
        "classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("area", sa.String(length=80), nullable=False),
        sa.Column("subarea", sa.String(length=120), nullable=True),
        sa.Column("topic", sa.String(length=160), nullable=True),
        sa.Column("subtopic", sa.String(length=160), nullable=True),
        sa.Column("competence", sa.String(length=160), nullable=True),
        sa.Column("skill", sa.String(length=160), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("requires_formula", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_graph", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_colombia_context", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("concepts_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("keywords_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("likely_error_types_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("classified_by", sa.String(length=80), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_classifications_question_id", "classifications", ["question_id"], unique=True)
    op.create_index("ix_classifications_topic", "classifications", ["topic"])
    op.create_index("ix_classifications_subarea", "classifications", ["subarea"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_answer", sa.String(length=1), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("time_seconds", sa.Integer(), nullable=True),
        sa.Column("error_type", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("review_after", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_attempts_question_id", "attempts", ["question_id"])
    op.create_index("ix_attempts_review_after", "attempts", ["review_after"])

    op.create_table(
        "study_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mode", sa.String(length=80), nullable=False),
        sa.Column("area", sa.String(length=80), nullable=True),
        sa.Column("topic", sa.String(length=160), nullable=True),
        sa.Column("questions_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "daily_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("available_minutes", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("plan_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_daily_plans_plan_date", "daily_plans", ["plan_date"])

    op.create_table(
        "question_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("embedding_model", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_question_embeddings_question_id", "question_embeddings", ["question_id"], unique=True)


def downgrade() -> None:
    op.drop_table("question_embeddings")
    op.drop_table("daily_plans")
    op.drop_table("study_sessions")
    op.drop_table("attempts")
    op.drop_table("classifications")
    op.drop_table("questions")
    op.drop_table("documents")
