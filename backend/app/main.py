from fastapi import FastAPI
from app.middleware.monitoring import MonitoringMiddleware
from app.middleware.rate_limiting import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.services import auth_service, websocket_service
from app.routers import document, chat
from app.utils.logging import setup_logging
import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from app.models.database import Base
from app.dependencies import engine

logger = setup_logging()

# ==========================================
# Keep-Alive Self-Ping (Hugging Face Spaces)
# ==========================================
KEEP_ALIVE_INTERVAL = int(os.getenv("KEEP_ALIVE_INTERVAL", "300"))  # 5 minutes
SELF_PING_URL = os.getenv("SELF_PING_URL", "http://localhost:8000/health")

async def keep_alive_task():
    """Background task that pings the health endpoint periodically
    to prevent Hugging Face Spaces from sleeping the container."""
    await asyncio.sleep(30)  # Initial delay to let the server fully start
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(SELF_PING_URL, timeout=10)
                logger.info(f"Keep-alive ping: status={response.status_code}")
            except Exception as e:
                logger.warning(f"Keep-alive ping failed: {e}")
            await asyncio.sleep(KEEP_ALIVE_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the PostgreSQL Database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    # Start the keep-alive background task
    logger.info(f"Starting keep-alive task (interval={KEEP_ALIVE_INTERVAL}s)")
    keep_alive = asyncio.create_task(keep_alive_task())

    yield

    # Cleanup on shutdown
    keep_alive.cancel()
    try:
        await keep_alive
    except asyncio.CancelledError:
        logger.info("Keep-alive task stopped.")

app = FastAPI(title="RAG System API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(MonitoringMiddleware)

app.include_router(auth_service.router)
app.include_router(websocket_service.router)
app.include_router(document.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the RAG System API"}

@app.get("/health")
def health_check():
    """Dedicated health check endpoint for keep-alive pings."""
    return {"status": "alive"}
