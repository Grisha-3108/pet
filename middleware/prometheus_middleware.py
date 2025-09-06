from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Histogram


class PrometheusMetrics(BaseHTTPMiddleware):
    request_proccess_time = Histogram('request_proccess_time', 
                                      'time of request proccessing', 
                                      ['endpoint'])

    async def dispatch(self, request: Request, call_next):
        time_start = perf_counter()
        response = await call_next(request)
        time_end = perf_counter()
        self.request_proccess_time.labels(request.url.path).observe(time_end - time_start)
        return response