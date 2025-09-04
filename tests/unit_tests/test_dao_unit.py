import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError

from dao.user_dao import UserDAO
from models import User, UserScope
from models.user_scope import Scope
from schemas.user import CreateUserSchema, ScopeSchema, UpdateUserSchema
from authorization.hashing import check_password


@pytest.mark.asyncio()
async def test_user_dao_create_and_delete_user():
    await UserDAO.create_user(CreateUserSchema(username='test_user@mail.ru', 
                                         password='test'))
    user: User = await UserDAO.get_by_filter(username='test_user@mail.ru')
    assert user is not None
    assert user.is_active
    assert not user.is_verified
    assert check_password('test', user.hashed_password)
    assert await UserDAO.delete_user(email='test_user@mail.ru')
    user: User = await UserDAO.get_by_filter(username='test_user@mail.ru')
    assert user is None


@pytest.mark.asyncio()
async def test_user_dao_grant_and_revoke_scope(async_session, simple_user):
    await UserDAO.grant_scopes('simple_user@mail.ru', [ScopeSchema(scope=Scope.update)])
    scope = await async_session.get(UserScope, ('3ce3d031-f9c2-435a-88a3-af406deeb2d1', Scope.update.name))
    assert scope
    await UserDAO.revoke_scopes('simple_user@mail.ru', [ScopeSchema(scope=Scope.update)])
    scope = await async_session.get(UserScope, ('3ce3d031-f9c2-435a-88a3-af406deeb2d1', Scope.update.name))
    assert not scope


@pytest.mark.asyncio
async def test_user_dao_create_new_user_with_already_used_email(simple_user):
    with pytest.raises(IntegrityError, match=r'duplicate key value violates unique constraint[.]*'):
        await UserDAO.create_user(CreateUserSchema(username='simple_user@mail.ru', 
                                            password='test'))

@pytest.mark.asyncio
async def test_user_dao_verify_user(simple_user):
    assert await UserDAO.activate_user('3ce3d031-f9c2-435a-88a3-af406deeb2d1')
    user = await UserDAO.get_by_uuid('3ce3d031-f9c2-435a-88a3-af406deeb2d1')
    assert user.is_verified


@pytest.mark.asyncio
async def test_user_dao_update_user(simple_user):
    await UserDAO.update_user('simple_user@mail.ru', UpdateUserSchema(username = 'not_simple_user@mail.ru', is_active=False))
    user = await UserDAO.get_by_filter(username='not_simple_user@mail.ru')
    assert user
    assert not user.is_active

@pytest.mark.asyncio
async def test_user_dao_delete_user(simple_user):
    assert await UserDAO.delete_user('simple_user@mail.ru')
    user = await UserDAO.get_by_filter(username='simple_user@mail.ru')
    assert not user