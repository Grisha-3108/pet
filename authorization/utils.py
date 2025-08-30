from datetime import (datetime, 
                      timezone,
                      timedelta)
from typing import Any

from fastapi import (HTTPException,
                     status)
from authorization.hashing import check_password
import jwt
from jwt.exceptions import InvalidTokenError
import aiofiles

from config import settings
from models import User
from dao.user_dao import UserDAO





async def create_token(payload: dict[str, Any], 
                 secret: str = settings.token.private_key,
                 expiration: timedelta = settings.token.access_token_expire) -> str:
    async with aiofiles.open(secret, mode='r') as key:
        key_str = await key.read()

    copy_payload = payload.copy()
    copy_payload.update({'exp' : (datetime.now(tz=timezone.utc).timestamp() 
                                  + expiration.total_seconds())})
    
    return jwt.encode(copy_payload, key_str, algorithm='RS256')

async def decode_token(token: str, 
                 secret: str = settings.token.public_key) -> dict[str, Any]:
    async with aiofiles.open(secret, mode='r') as key:
        key_str = await key.read()

    try:
        data = jwt.decode(token, key_str, algorithms=['RS256'])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Токен не валиден')
    
    return data


async def authenticate_user(username: str, password: str, scopes: list[str] | None) -> User:
    user: User = await UserDAO.get_by_filter(username=username)
    if scopes:
        authenticate_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Имя пользователя или пароль или права доступа неверны!',
                            headers={'WWW-Authenticate': f'Bearer scope="{' '.join(scopes)}"'})
    else:
        authenticate_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Имя пользователя или пароль или права доступа неверны!',
                            headers={'WWW-Authenticate': 'Bearer'})
    if not user:
        raise authenticate_error
    if not check_password(password, user.hashed_password):
        raise authenticate_error
    
    user_scopes = [scope.scope for scope in user.scopes]
    for scope in scopes:
        if scope not in user_scopes:
            raise authenticate_error
    return user