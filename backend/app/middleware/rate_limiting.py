from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Usage in routes:
# @app.post("/api/chat")
# @limiter.limit("10/minute")
# async def chat_with_documents(request: Request, ...):
