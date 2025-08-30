import uuid
import enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID, Enum
from sqlalchemy.schema import ForeignKey, PrimaryKeyConstraint

from models import Base

if TYPE_CHECKING:
    from models.user import User


class Scope(enum.Enum):
    update = 'Редактирование пользователей'
    delete = 'Удаление пользователей'
    modify_scope = 'Управлять правами'


class UserScope(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, 
                                               ForeignKey('users.id', ondelete='CASCADE', name='user_id_fk'), 
                                               nullable=False)
    scope: Mapped[Scope] = mapped_column(Enum(Scope), nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='User.scopes', foreign_keys=[user_id])

    __table_args__ = (
        PrimaryKeyConstraint(user_id, scope, name='user_scopes_pk'),
    )