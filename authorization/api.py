from typing import Annotated
import uuid

from fastapi import (APIRouter, 
                     BackgroundTasks,
                     Depends, HTTPException,
                     status)
from fastapi.security import OAuth2PasswordRequestForm

from models.user_scope import Scope
from dao.user_dao import UserDAO
from config import settings
from schemas.user import (CreateUserScheme, 
                          UserReadScheme,
                          UpdateUserSchema,
                          RequestVerifySchema,
                          VerifySchema)
from .utils import authenticate_user, create_token, decode_token
from models import User
from authorization.mail import send_verify_request
from .dependencies import get_user

auth_router = APIRouter(prefix=settings.auth_prefix, 
                        tags=['Auth'])


@auth_router.post('/register',
                  response_model=UserReadScheme)
async def register(user_data: CreateUserScheme):
    user = await UserDAO.create_user(user_data)
    return UserReadScheme.model_validate(user)


@auth_router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user: User = await authenticate_user(form_data.username, 
                                         form_data.password, 
                                         form_data.scopes)
    token_data = {'sub': str(user.id), 
                  'scopes': form_data.scopes}
    access_token = await create_token(token_data)
    return {'access_token': access_token, 
            'token_type' : 'Bearer'}



@auth_router.post('/verify-request')
async def verify_request(verify: RequestVerifySchema):
    verify_error = HTTPException(status_code=status.HTTP_409_CONFLICT,
                                 detail='Пользователя с таким email не существует или он уже активирован или он не активен')
    user: User = await UserDAO.get_by_filter(username=verify.email)
    if not user:
        raise verify_error
    if not user.is_active or user.is_verified:
        raise verify_error
    token_data = {'sub': str(user.id)}
    token = await create_token(token_data, 
                               expiration=settings.email.verify_token_exp)
    await send_verify_request(verify.email, token)
    return {'request_sended_to': verify.email}

@auth_router.post('/verify')
async def verify(token: VerifySchema):
    payload = await decode_token(token=token.verify_token)
    return await UserDAO.activate_user(uuid.UUID(payload['sub']))


@auth_router.get('/me')
async def me(user = Depends(get_user())):
    return UserReadScheme.model_validate(user)