from fastapi.security import (OAuth2PasswordBearer,
                              SecurityScopes)
from fastapi import Depends, HTTPException, status

from config import settings
from models.user_scope import Scope
from models import User
from dao.user_dao import UserDAO
from authorization.utils import decode_token


oauth_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.auth_prefix}/login',
                                    description='Авторизация по логину и паролю',
                                    scopes={e.name: e.value for e in Scope})

def get_user(active: bool = False, 
             verified: bool = False):
    async def get(scopes: SecurityScopes, 
                token: str = Depends(oauth_scheme)) -> User:
        forbidden = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='У вас не хватае прав или пользователь не активен или не верифицирован')
        not_auth = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Пользователь не существует')
        payload = await decode_token(token)

        payload_scopes = payload['scopes']
        for scope in scopes.scopes:
            if scope not in payload_scopes:
                raise forbidden

        user: User = await UserDAO.get_by_uuid(payload['sub'])
        if not user:
            raise not_auth
        if active and not user.is_active:
            raise forbidden
        if verified and not user.is_verified:
            raise forbidden
        return user
    return get