from contextlib import asynccontextmanager
import logging
import os


from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from prometheus_client import multiprocess

from authorization.api import auth_router
from database import async_engine
from producers.utils import close_connection
from config import settings
from middleware import metrics_router, PrometheusMetrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)s %(levelname)s %(funcName)s %(lineno)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    yield
    await async_engine.dispose()
    await close_connection()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.add_middleware(PrometheusMetrics)
app.include_router(metrics_router)
app.add_middleware(CORSMiddleware,
                   allow_credentials=False,
                   allow_origins=['*'],
                   allow_methods=['GET', 'POST', 'PATCH'],
                   allow_headers=['*'])
app.include_router(router=auth_router)

@app.get('/ping')
def ping_route():
    return {'message': 'ok'}


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level
    )