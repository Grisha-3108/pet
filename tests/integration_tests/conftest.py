from typing import AsyncGenerator
import pytest_asyncio
import aio_pika

from config import settings
from models import User
from authorization.hashing import hash_password

@pytest_asyncio.fixture()
async def simple_user(async_session):
    user = User(id='3ce3d031-f9c2-435a-88a3-af406deeb2d1',
         username='simple_user@mail.ru',
         hashed_password=hash_password('password'))
    async_session.add(user)
    await async_session.commit()
    yield
    await async_session.delete(user)
    await async_session.commit()


@pytest_asyncio.fixture(scope='session')
async def rabbit_connection() -> AsyncGenerator[aio_pika.abc.AbstractConnection, None]:
    connection = await aio_pika.connect(settings.test_rabbitmq.connection)
    async with connection:
        yield connection


@pytest_asyncio.fixture()
async def rabbit_channel(rabbit_connection):
    channel = await rabbit_connection.channel(publisher_confirms = True, 
                                              on_return_raises = True)
    async with channel:
        yield channel


@pytest_asyncio.fixture()
async def login_queue(rabbit_channel, scope='session'):
    queue = await rabbit_channel.declare_queue(settings.test_rabbitmq.login_queue, 
                                               durable=True)
    yield queue
    await queue.delete(if_empty = False, 
                       if_unused = False)


@pytest_asyncio.fixture()
async def logout_queue(rabbit_channel, scope='session'):
    queue = await rabbit_channel.declare_queue(settings.test_rabbitmq.logout_queue,
                                               durable = True)
    yield queue
    await queue.delete(if_empty = False, 
                       if_unused = False)
