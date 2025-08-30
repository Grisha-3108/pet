from pydantic import BaseModel, EmailStr, Field

from models import UserScope
from models.user_scope import UserScope


class ScopeScheme(BaseModel):
    scope: UserScope


class CreateUserScheme(BaseModel):
    username: EmailStr = Field(max_length=100)
    hashed_password: str = Field(max_length=60)


class UpdateUserSchema(BaseModel):
    username: EmailStr | None = Field(max_length=100, default=None)
    hashed_password: str | None = Field(max_length=60, default=None)
    is_active: bool | None = Field(default=None)
    is_verified: bool | None = Field(default=None)