import uuid

from models import Base 
from database import async_session_factory
from sqlalchemy.sql import select


class BaseDAO:
    model = Base
    async_session_factory = async_session_factory

    @classmethod
    async def get_by_uuid(cls, id: uuid.UUID) -> model | None:
        async with cls.async_session_factory() as async_session:
            item = await async_session.get(cls.model, id)
        return item
        
    @classmethod
    async def get_by_filter(cls, **filter) -> model | None:
        async with cls.async_session_factory() as async_session:
            query = select(cls.model).filter_by(**filter)
            item = await async_session.scalar(query)
        return item