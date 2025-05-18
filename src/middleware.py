# src/middleware.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from src.logger import request_logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            request_logger.info(f"Response: {response.status_code} in {round(process_time * 1000, 2)} ms")
            return response
        except Exception as exc:
            request_logger.error(f"Request failed: {str(exc)}")
            raise 