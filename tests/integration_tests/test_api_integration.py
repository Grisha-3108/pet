import pytest
import pydantic

from models.user_scope import Scope
from producers.login_producer import LoginMessage
from producers.logout_producer import LogoutMessage
from config import settings

from dao.user_dao import UserDAO
from models import User, UserScope
from models.user_scope import Scope
from schemas.user import EmailWithScopesSchema, ScopeSchema

@pytest.mark.asyncio
@pytest.mark.parametrize('test_client',
                         [(' '.join([scope.name for scope in Scope]))],
                         indirect=['test_client'])
async def test_grant_and_revoke_scopes_by_admin(test_client, simple_user, login_queue, logout_queue):
    login_message = await login_queue.get()
    login = LoginMessage.model_validate_json(login_message.body)
    assert login.username == 'Grisha-3108@yandex.ru'

    grant = await test_client.post(str(settings.auth_prefix) + '/grant-scope', 
                                   json={'email': 'simple_user@mail.ru', 'scopes': [{'scope': Scope.modify_scope.value}]})
    print(grant.json())
    assert grant.status_code == 200
    assert grant.json() == {'email': 'simple_user@mail.ru', 'grant_scopes': [{'scope': Scope.modify_scope.value}]}

    revoke = await test_client.post(str(settings.auth_prefix) + '/revoke-scope',
                                    json={'email': 'simple_user@mail.ru', 'scopes': [{'scope': Scope.modify_scope.value}]})
    assert revoke.status_code == 200
    assert revoke.json() == {'email': 'simple_user@mail.ru', 'revoke_scopes': [{'scope': Scope.modify_scope.value}]}
    
    await test_client.post(str(settings.auth_prefix) + '/logout')
    logout_message = await logout_queue.get()
    login = LogoutMessage.model_validate_json(logout_message.body)
    assert login.username == 'Grisha-3108@yandex.ru'