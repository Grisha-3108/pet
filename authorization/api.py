from typing import Annotated

from fastapi import (APIRouter, 
                     BackgroundTasks,
                     Depends)
from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)

from models.user_scope import Scope
from dao.user_dao import UserDAO
from config import settings
from schemas.user import (CreateUserScheme, 
                          UserReadScheme,
                          UpdateUserSchema)
from .utils import authenticate_user, create_token
from models import User

oauth_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.auth_prefix}/login',
                                    description='Авторизация по логину и паролю',
                                    scopes={e.name: e.value for e in Scope})

auth_router = APIRouter(prefix=settings.auth_prefix, 
                        tags=['Auth'])


@auth_router.post('/register',
                  response_model=UserReadScheme)
async def register(user_data: CreateUserScheme):
    user = await UserDAO.create_user(user_data)
    return UserReadScheme(id=user.id, 
                          username=user.username, 
                          is_active=user.is_active,
                          is_verified=user.is_verified)


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


@auth_router.get('/token')
async def get_token(token: str = Depends(oauth_scheme)):
    return {'token': token}