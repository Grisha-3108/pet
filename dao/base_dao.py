import uuid

from models import Base
from database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select


class BaseDAO:
    model = Base
    async_session_factory = async_session_factory

    @classmethod
    async def get_by_uuid(cls, id: uuid.UUID) -> model | None:
        async with cls.async_session_factory() as async_session:
            return await async_session.get(cls.model, id)
        
    @classmethod
    async def get_by_filter(cls, **filter) -> model | None:
        async with cls.async_session_factory() as async_session:
            query = select(cls.model).filter_by(**filter)
            res = await async_session.scalars(query)
            item = res.one_or_none()
            return item