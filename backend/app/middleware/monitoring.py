from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger('rag_system')

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor request performance"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info({
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'process_time_ms': round(process_time * 1000, 2)
        })
        
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
