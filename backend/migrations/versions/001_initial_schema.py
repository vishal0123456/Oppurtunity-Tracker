"""Initial schema — opportunities and user_applications tables

Revision ID: 001
Revises: 
Create Date: 2026-05-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("organization", sa.String(300)),
        sa.Column("description", sa.Text),
        sa.Column("category", sa.String(100)),
        sa.Column("tags", postgresql.ARRAY(sa.String), default=list),
        sa.Column("country", postgresql.ARRAY(sa.String), default=list),
        sa.Column("is_remote", sa.Boolean, default=False),
        sa.Column("women_friendly", sa.Boolean, default=False),
        sa.Column("india_eligible", sa.Boolean, default=False),
        sa.Column("student_eligible", sa.Boolean, default=False),
        sa.Column("age_limit", sa.String(100)),
        sa.Column("eligibility", sa.Text),
        sa.Column("funding_amount", sa.String(200)),
        sa.Column("application_fee", sa.String(100)),
        sa.Column("link", sa.String(2000), unique=True, nullable=False),
        sa.Column("source_url", sa.String(2000)),
        sa.Column("source_name", sa.String(200)),
        sa.Column("deadline", sa.Date),
        sa.Column("is_expired", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_opportunities_title", "opportunities", ["title"])
    op.create_index("ix_opportunities_category", "opportunities", ["category"])
    op.create_index("ix_opportunities_deadline", "opportunities", ["deadline"])
    op.create_index("ix_opportunities_is_expired", "opportunities", ["is_expired"])
    op.create_index("ix_opportunities_link", "opportunities", ["link"])
    op.create_index("ix_opportunities_women_friendly", "opportunities", ["women_friendly"])
    op.create_index("ix_opportunities_india_eligible", "opportunities", ["india_eligible"])
    op.create_index("ix_opportunities_student_eligible", "opportunities", ["student_eligible"])

    op.create_table(
        "user_applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), default="saved", nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("priority", sa.Integer, default=3),
        sa.Column("applied_at", sa.Date),
        sa.Column("reminder_date", sa.Date),
        sa.Column("document_links", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_applications_opportunity_id", "user_applications", ["opportunity_id"])
    op.create_index("ix_user_applications_status", "user_applications", ["status"])


def downgrade() -> None:
    op.drop_table("user_applications")
    op.drop_table("opportunities")
