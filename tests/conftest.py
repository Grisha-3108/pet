import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (create_async_engine, 
                                    async_sessionmaker,
                                    AsyncEngine,
                                    AsyncSession)
import httpx
import aio_pika

from config import settings
from models.base import Base
from main import app


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
def check_test_mode():
    assert settings.test_mode


@pytest_asyncio.fixture(scope='session')
async def db() -> AsyncGenerator[AsyncEngine, None]:
    async_engine = create_async_engine(url=settings.test_db.async_connection, 
                                       connect_args={'ssl': settings.test_db.sslmode})
    async with async_engine.begin() as engine:
        engine.run_sync(Base.metadata.drop_all)
        engine.run_sync(Base.metadata.create_all)

    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def async_session_factory(db):
    async_factory = async_sessionmaker(bind=db, 
                                       autoflush=False, 
                                       autocommit=False, 
                                       expire_on_commit=False)
    return async_factory


@pytest_asyncio.fixture(scope='function')
async def async_session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), 
                                 base_url=settings.test_base_url) as client:
        yield client


@pytest_asyncio.fixture(scope='session')
async def rabbit_connection() -> AsyncGenerator[aio_pika.abc.AbstractConnection, None]:
    connection = await aio_pika.connect(settings.test_rabbit.connection)
    async with connection:
        yield connection

@pytest_asyncio.fixture()
async def rabbit_channel(rabbit_connection):
    channel = await rabbit_connection.channel(sender_confirms = True)
    async with channel:
        yield channel


@pytest_asyncio.fixture()
async def get_message(request, rabbit_channel):
    queue = await rabbit_channel.declare_queue(request.param)
    try:
        msg = await queue.get(no_ack=True)
    except aio_pika.exceptions.QueueEmpty:
        msg = None
    await queue.purge()
    return msg