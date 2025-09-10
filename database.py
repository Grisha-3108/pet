from ssl import create_default_context
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from config import settings

if settings.test_mode:
    async_engine = create_async_engine(url=settings.test_db.async_connection, 
                                       isolation_level = settings.test_db.isolation_level,
                                       connect_args = {'ssl': create_default_context() if settings.test_db.sslmode else 'disable'})
else:
    async_engine = create_async_engine(url=settings.db.async_connection, 
                                       isolation_level = settings.db.isolation_level,
                                       connect_args = {'ssl': create_default_context() if settings.test_db.sslmode else 'disable'})


async_session_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)