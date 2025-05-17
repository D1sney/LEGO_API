"""add_refresh_tokens_table

Revision ID: a6638baa1e8f
Revises: 120460941387
Create Date: 2025-05-17 14:33:35.550157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'a6638baa1e8f'
down_revision: Union[str, None] = '120460941387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('token', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('revoked', sa.Boolean(), default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('refresh_tokens')
