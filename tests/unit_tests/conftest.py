import pytest_asyncio

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
