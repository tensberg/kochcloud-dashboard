"""create wireguard_client schema

Revision ID: 7e82df7a6782
Revises: 63be430581f7
Create Date: 2026-02-12 14:49:55.361624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence

# revision identifiers, used by Alembic.
revision: str = '7e82df7a6782'
down_revision: Union[str, Sequence[str], None] = '63be430581f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ip_octet_seq = Sequence("wireguard_client_ip_octet_seq", start=2, maxvalue=254)  # start at 2, .1 is server

def upgrade() -> None:
    """Upgrade schema."""
    op.execute(CreateSequence(ip_octet_seq))
    op.create_table(
        'wireguard_client',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ip_octet', sa.Integer(), nullable=False, unique=True, server_default=ip_octet_seq.next_value()),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('private_key', sa.String(), nullable=False),
        sa.Column('public_key', sa.String(), nullable=False),
        sa.Column('psk', sa.String(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('wireguard_client')
    op.execute(DropSequence(ip_octet_seq))