"""create app-passwords schema

Revision ID: 63be430581f7
Revises: 
Create Date: 2026-01-04 18:21:17.223157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '63be430581f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sub', sa.String(), nullable=False, unique=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        'token',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('app', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('hash', sa.String(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('token')
    op.drop_table('user')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
