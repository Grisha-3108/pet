import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID, String, Boolean

from models import Base

if TYPE_CHECKING:
    from models.user_scope import UserScope


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=str(True))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=str(True))

    scopes: Mapped[List['UserScope']] = relationship('UserScope', 
                                                   back_populates='UserScope.user', 
                                                   lazy='subquery')