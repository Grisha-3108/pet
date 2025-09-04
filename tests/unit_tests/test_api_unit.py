import uuid

import pytest
from pytest import param

from models import User
from authorization.hashing import hash_password
from config import settings
from models.user_scope import Scope

from schemas.user import CreateUserSchema

@pytest.mark.asyncio
@pytest.mark.parametrize('test_client, username, password, status_code',
                         [
                            param('', 'Grun@mail.ru', '11223344', 200, id='Valid user')
                         ], indirect=['test_client'])
async def test_register_router_valid_user(mocker, test_client, username, password, status_code):
    pass
    mocked_get_by_filter = mocker.patch('authorization.api.UserDAO.get_by_filter')
    mocked_get_by_filter.return_value = None
    mocked_create_user = mocker.patch('authorization.api.UserDAO.create_user')
    mocked_create_user.return_value = user = User(id=uuid.uuid4(),
                                                  username = username, 
                                                  hashed_password = hash_password(password),
                                                  scopes=[],
                                                  is_active = True,
                                                  is_verified = False)
    response = await test_client.post(settings.auth_prefix + '/register', 
                                      json={'username': username, 
                                            'password': password})
    mocked_get_by_filter.assert_awaited_once_with(username=username)
    mocked_create_user.assert_awaited_once_with(CreateUserSchema(username=username,
                                                                 password=password))
    assert response.status_code == status_code
    assert response.json() == {'id': str(user.id), 'username': username, 'is_active': True, 'is_verified': False, 'scopes': []}

@pytest.mark.asyncio
@pytest.mark.parametrize('test_client, username, password, status_code',
                         [
                            param('', 'Grun', '11223344', 422, id='Invalid user')
                         ], indirect=['test_client'])
async def test_register_router_invalid_user(mocker, test_client, username, password, status_code):
    mocked_get_by_filter = mocker.patch('authorization.api.UserDAO.get_by_filter')
    mocked_get_by_filter.return_value = None
    mocked_create_user = mocker.patch('authorization.api.UserDAO.create_user')
    mocked_create_user.return_value = user = User(id=uuid.uuid4(),
                                                  username = username, 
                                                  hashed_password = hash_password(password),
                                                  scopes=[],
                                                  is_active = True,
                                                  is_verified = False)
    response = await test_client.post(settings.auth_prefix + '/register', 
                                      json={'username': username, 
                                            'password': password})
    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize('test_client',
                         [''],
                         indirect=['test_client'])
async def test_login_router_correct_credentials(test_client, simple_user):
    response = await test_client.post(settings.auth_prefix + '/login',
                                data={'grant_type': 'password',
                                      'username': 'simple_user@mail.ru', 
                                      'password': 'password',
                                      'scope': ''})
    assert response.status_code == 200
    data = response.json()
    assert data.get('token_type') in ('bearer', 'Bearer')
    assert data.get('access_token')
    assert isinstance(data.get('access_token'), str)
    assert len(data.get('access_token')) > 1
    
@pytest.mark.asyncio
@pytest.mark.parametrize('test_client',
                         [''],
                         indirect=['test_client'])
async def test_login_router_user_does_not_exists(test_client, simple_user):

    response = await test_client.post(settings.auth_prefix + '/login',
                                data={'grant_type': 'password',
                                      'username': 'unexist_user@mail.ru', 
                                      'password': 'password',
                                      'scope': ''})
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize('test_client',
                         [''],
                         indirect=['test_client'])
async def test_login_router_user_do_not_have_scopes(test_client, simple_user):

    response = await test_client.post(settings.auth_prefix + '/login',
                                data={'grant_type': 'password',
                                      'username': 'unexist_user@mail.ru', 
                                      'password': 'password',
                                      'scope': Scope.modify_scope.name})
    assert response.status_code == 401