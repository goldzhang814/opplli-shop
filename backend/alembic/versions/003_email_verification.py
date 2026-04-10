"""add email_verification_codes table

Revision ID: 003
Revises: 002
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'email_verification_codes',
        sa.Column('id',         sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column('email',      sa.String(191),   nullable=False, index=True),
        sa.Column('code',       sa.String(6),     nullable=False),
        sa.Column('purpose',    sa.String(20),    nullable=False, server_default='register'),
        sa.Column('is_used',    sa.Boolean(),     nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(),    nullable=False),
        sa.Column('created_at', sa.DateTime(),    server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('email_verification_codes')