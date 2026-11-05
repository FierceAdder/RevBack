"""add processed_payments for idempotent Razorpay webhooks

Revision ID: c3d9e2f1a7b4
Revises: bac90e17a02c
Create Date: 2026-10-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d9e2f1a7b4'
down_revision: Union[str, Sequence[str], None] = 'bac90e17a02c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'processed_payments',
        sa.Column('payment_id', sa.String(length=64), nullable=False),
        sa.Column('invoice_id', sa.String(length=36), nullable=False),
        sa.Column('event', sa.String(length=64), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('payment_id'),
    )
    op.create_index(op.f('ix_processed_payments_invoice_id'), 'processed_payments', ['invoice_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_processed_payments_invoice_id'), table_name='processed_payments')
    op.drop_table('processed_payments')
