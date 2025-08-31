import uuid
from typing import Annotated

from pydantic import (BaseModel, 
                      EmailStr, 
                      Field, 
                      ConfigDict)

from models.user_scope import Scope


class ScopeScheme(BaseModel):
    scope: Scope
    model_config = ConfigDict(from_attributes=True)


class CreateUserScheme(BaseModel):
    username: EmailStr = Field(max_length=100)
    password: str = Field(max_length=60)



class UserReadScheme(BaseModel):
    id: uuid.UUID
    username: EmailStr = Field(max_length=100)
    is_active: bool
    is_verified: bool
    scopes: list[ScopeScheme] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

    

class UpdateUserSchema(BaseModel):
    username: EmailStr | None = Field(max_length=100, default=None)
    hashed_password: str | None = Field(max_length=60, default=None)
    is_active: bool | None = Field(default=None)
    is_verified: bool | None = Field(default=None)


class RequestVerifySchema(BaseModel):
    email: EmailStr = Field(max_length=100)

class VerifySchema(BaseModel):
    verify_token: str