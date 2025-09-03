
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from config import settings

if settings.test_mode:
    async_engine = create_async_engine(url=settings.test_db.async_connection, 
                                       isolation_level = settings.test_db.isolation_level,
                                       connect_args = {'ssl': settings.test_db.sslmode})
else:
    async_engine = create_async_engine(url=settings.db.async_connection, 
                                       isolation_level = settings.db.isolation_level,
                                       connect_args = {'ssl': settings.db.sslmode})


async_session_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)