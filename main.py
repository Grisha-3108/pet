from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from authorization.api import auth_router
from database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)s %(levelname)s %(funcName)s %(lineno)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(router=auth_router)


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True
    )
