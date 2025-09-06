import secrets
import os

from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, multiprocess
from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import settings

metrics_router = APIRouter(tags=['prometheus'])
basic_scheme = HTTPBasic()

@metrics_router.get(settings.prometheus.endpoint)
def metrics(credentials: HTTPBasicCredentials = Depends(basic_scheme)):
    if (not secrets.compare_digest(credentials.username.encode(),
                                  settings.prometheus.username.encode())
        or not secrets.compare_digest(credentials.password.encode(),
                                  settings.prometheus.password.encode())):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверный логин или пароль')
    if os.getenv('PROMETHEUS_MULTIPROC_DIR'):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
    data = generate_latest()
    return_headers = {'Content-Type': CONTENT_TYPE_LATEST,
                        'Content-Length': str(len(data))}
        
    return Response(content=data, headers=return_headers)