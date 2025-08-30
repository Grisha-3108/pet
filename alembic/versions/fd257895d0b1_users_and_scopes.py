"""Users and scopes

Revision ID: fd257895d0b1
Revises: 
Create Date: 2025-08-30 12:44:39.172312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd257895d0b1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.Column('is_verified', sa.Boolean(), server_default='True', nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_scopes',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('scope', sa.Enum('update', 'delete', 'modify_scope', name='scope'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_id_fk', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'scope', name='user_scopes_pk')
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_scopes')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS scope')
