"""create app-passwords schema

Revision ID: 63be430581f7
Revises: 
Create Date: 2026-01-04 18:21:17.223157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63be430581f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sub', sa.String(), nullable=False, unique=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'token',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer()),
        sa.Column('app', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('hash', sa.String(), nullable=False),
        sa.Column('expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('token')
    op.drop_table('user')
