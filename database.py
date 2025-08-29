from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


async_engine = create_async_engine(url=settings.db.async_connection, 
                                   isolation_level = settings.db.isolation_level,
                                   connect_args = {'sslmode': settings.db.sslmode})


sync_engine = create_engine(url=settings.db.sync_connection, 
                                  isolation_level = settings.db.isolation_level,
                                  connect_args = {'sslmode': settings.db.sslmode})


async_session_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


sync_session_factory = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)