import uuid

from models import Base
from database import async_session_factory

class BaseDAO:
    model = Base
    async_session_factory = async_session_factory

    @classmethod
    async def get_by_uuid(cls, id: uuid.UUID) -> model | None:
        async with cls.async_session_factory() as async_session:
            return await async_session.get(cls.model, id)