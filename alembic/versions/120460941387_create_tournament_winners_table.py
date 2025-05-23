"""Create tournament winners table

Revision ID: 120460941387
Revises: 5e0a1434d99c
Create Date: 2025-05-15 14:16:34.036850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '120460941387'
down_revision: Union[str, None] = '5e0a1434d99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tournament_winners',
    sa.Column('winner_id', sa.Integer(), nullable=False),
    sa.Column('tournament_id', sa.Integer(), nullable=False),
    sa.Column('set_id', sa.Integer(), nullable=True),
    sa.Column('minifigure_id', sa.String(), nullable=True),
    sa.Column('total_votes', sa.Integer(), nullable=True),
    sa.Column('won_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('(set_id IS NOT NULL AND minifigure_id IS NULL) OR (set_id IS NULL AND minifigure_id IS NOT NULL)'),
    sa.ForeignKeyConstraint(['minifigure_id'], ['minifigures.minifigure_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['set_id'], ['sets.set_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.tournament_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('winner_id'),
    sa.UniqueConstraint('tournament_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tournament_winners')
    # ### end Alembic commands ###
