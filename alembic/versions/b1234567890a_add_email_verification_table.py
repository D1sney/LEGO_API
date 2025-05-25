"""add_email_verification_table

Revision ID: b1234567890a
Revises: a6638baa1e8f
Create Date: 2025-05-17 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'b1234567890a'
down_revision: Union[str, None] = 'a6638baa1e8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'email_verifications',
        sa.Column('email', sa.String(), primary_key=True, index=True),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('verification_code', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('verified', sa.Boolean(), default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('email_verifications') 