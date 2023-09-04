from fastapi import Request, Response, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import time


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, digits: int = 3, header: str = "X-Response-Time", suffix: bool = True, custom_fn=None):
        super().__init__(app)
        self.digits = digits
        self.header = header
        self.suffix = "ms" if suffix else ""
        self.custom_fn = custom_fn

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        elapsed_time = (time.time() - start_time) * \
            1000  # Convert to milliseconds
        value = f"{elapsed_time:.{self.digits}f}{self.suffix}"

        if self.custom_fn:
            self.custom_fn(request, response, elapsed_time)
        else:
            response.headers[self.header] = value

        return response
