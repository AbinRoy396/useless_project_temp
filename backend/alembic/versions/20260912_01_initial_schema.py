"""Initial Campus Voice schema."""
from alembic import op
import sqlalchemy as sa

revision = "20260912_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("complaints", sa.Column("id", sa.Integer, primary_key=True), sa.Column("anonymous_id", sa.String(16), nullable=False), sa.Column("department", sa.String(60), nullable=False), sa.Column("message", sa.Text, nullable=False), sa.Column("mood", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("category", sa.String(50), nullable=False), sa.Column("sentiment", sa.String(30), nullable=False), sa.Column("severity", sa.Integer, nullable=False), sa.Column("frustration_score", sa.Float, nullable=False), sa.Column("ai_summary", sa.String(280), nullable=False))
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])
    op.create_index("ix_complaints_category", "complaints", ["category"])
    op.create_index("ix_complaints_department", "complaints", ["department"])
    op.create_table("report_audits", sa.Column("id", sa.Integer, primary_key=True), sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("approved_by", sa.String(80), nullable=False), sa.Column("recipient", sa.String(320), nullable=False), sa.Column("subject", sa.String(240), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("provider_message_id", sa.String(120)), sa.Column("error_message", sa.String(500)))
    op.create_index("ix_report_audits_created_at", "report_audits", ["created_at"])

def downgrade():
    op.drop_table("report_audits")
    op.drop_table("complaints")
