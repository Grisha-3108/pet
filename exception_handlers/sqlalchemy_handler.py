from main import app

from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import (IntegrityError, 
                            InvalidRequestError)


@app.exception_handler(IntegrityError)
async def integrity_handler(request: Request, exc: IntegrityError):
    return ORJSONResponse(status_code=status.HTTP_409_CONFLICT,
                          content={'error': ('Нарушены ограничения целостности при выполнении операций' 
                                   ' с базой данных, проверьте уникальность первичного ключа, полей, для которых'
                                   ' значечения должно быть уникальным, а также существование значений для полей, '
                                   'которые являются внешними ключами, а также допустимость длин строк')})

@app.exception_handler(InvalidRequestError)
async def invalid_request_handler(request: Request, exc: InvalidRequestError):
    return ORJSONResponse(status_code=status.HTTP_409_CONFLICT,
                          content={'error': 'Синтаксическая ошибка в запросе. Проверьте значения параметров'})