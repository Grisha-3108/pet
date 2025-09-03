from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (AsyncSession)
import httpx
import aio_pika

from authorization.hashing import hash_password
from config import settings
from models.base import Base
from models.user import User
from models.user_scope import Scope, UserScope
from main import app
from database import async_session_factory, async_engine


@pytest_asyncio.fixture(autouse=True, scope='session')
async def init_test_environment():
    assert settings.test_mode
    async with async_engine.begin() as engine:
        await engine.run_sync(Base.metadata.drop_all)
        await engine.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


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


@pytest_asyncio.fixture(scope='session')
async def db_admin(async_session):
    admin = User(username = 'Grisha-3108@yandex.ru',
                 hashed_password = hash_password('11223344'),
                 is_active = True,
                 is_verified = True)
    admin.scopes.extend([UserScope(scope = scope) for scope in Scope])
    async_session.add(admin)
    await async_session.commit()


@pytest_asyncio.fixture(scope='session')
async def test_client(request, db_admin) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), 
                                 base_url=settings.test_base_url) as client:
        response = await client.post(settings.auth_prefix + '/login', 
                                     data={'grant_type': 'password',
                                           'username': 'Grisha-3108@yandex.ru', 
                                           'password': '11223344',
                                           'scope': request.param[0]})
        credentials = response.json()
        assert credentials.get('token_type') in ('Bearer', 'bearer')
        assert credentials.get('access_token') is not None
        client.headers['Authorization'] = f'Bearer {credentials.get('access_token')}'
        yield client