# middlewares/timing.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log only for specific paths or methods if needed
        print(f"{request.method} {request.url.path} took {duration:.3f}s")

        return response
