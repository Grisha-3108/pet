import uuid
from typing import Literal
import logging

from sqlalchemy import select

from dao.base_dao import BaseDAO
from models import User, UserScope
from schemas.user import (CreateUserSchema,
                          ScopeSchema,
                          UpdateUserSchema)
from authorization.hashing import hash_password


class UserDAO(BaseDAO):
    model = User
        
    @classmethod
    async def create_user(cls, user: CreateUserSchema) -> model:
        user_db = cls.model(username = user.username,
                            hashed_password = hash_password(user.password))
        async with cls.async_session_factory() as async_session:
            async_session.add(user_db)
            await async_session.commit()
            await async_session.refresh(user_db)
        return user_db
        
    @classmethod
    async def grant_scopes(cls, email: str, scopes: list[ScopeSchema]) -> Literal[True]:
        async with cls.async_session_factory() as async_session:
            query = select(User).filter_by(username=email)
            user = await async_session.scalar(query)
            for scope in scopes:
                user.scopes.append(UserScope(scope=scope.scope))
            await async_session.commit()
        return True
    
    @classmethod
    async def revoke_scopes(cls, email: str, scopes: list[ScopeSchema]) -> Literal[True]:
        async with cls.async_session_factory() as async_session:
            query = select(User).filter_by(username=email)
            user = await async_session.scalar(query)
            user.scopes = [user_scope for user_scope in user.scopes if user_scope.scope 
                           not in [scope.scope for scope in scopes]]
            await async_session.commit()
        return True
    
    @classmethod
    async def update_user(cls, email: str, new: UpdateUserSchema) -> model:
        async with cls.async_session_factory() as async_session:
            query = select(User).filter_by(username=email)
            user = await async_session.scalar(query)
            for attr, value in new.model_dump(exclude_none=True).items():
                setattr(user, attr, value)
            await async_session.commit()
            await async_session.refresh(user)
            return user
        
    @classmethod
    async def delete_user(cls, email: str) -> Literal[True]:
        async with cls.async_session_factory() as async_session:
            query = select(cls.model).filter_by(username=email)
            user = await async_session.scalar(query)
            if user:
                await async_session.delete(user)
                await async_session.commit()
        return True
        
    @classmethod 
    async def activate_user(cls, id: uuid.UUID) -> Literal[True]:
        async with cls.async_session_factory() as async_session:
            user = await async_session.get(cls.model, id)
            user.is_verified = True
            await async_session.commit()
        return True
    