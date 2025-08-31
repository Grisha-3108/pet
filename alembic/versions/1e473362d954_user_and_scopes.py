"""User and scopes

Revision ID: 1e473362d954
Revises: 
Create Date: 2025-08-31 12:38:32.832844

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

from models.user_scope import Scope
from models import User, UserScope
from authorization.hashing import hash_password

# revision identifiers, used by Alembic.
revision: str = '1e473362d954'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=60), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=False),
    sa.Column('is_verified', sa.Boolean(), server_default='False', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user_scopes',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('scope', sa.Enum('update', 'delete', 'modify_scope', name='scope'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_id_fk', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'scope', name='user_scopes_pk')
    )

    user_id = uuid.uuid4()
    op.bulk_insert(User.__table__, [{'id': user_id, 
                             'username': 'Grisha-3108@yandex.ru',
                             'hashed_password': hash_password('11223344'),
                             'is_active': True,
                             'is_verified': True}])
    op.bulk_insert(UserScope.__table__, [{'user_id': user_id, 'scope': Scope.modify_scope.name},
                   {'user_id': str(user_id), 'scope': Scope.delete.name},
                   {'user_id': str(user_id), 'scope': Scope.update.name}])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_scopes')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS scope')
