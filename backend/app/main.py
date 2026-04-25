from fastapi import FastAPI
from app.middleware.monitoring import MonitoringMiddleware
from app.middleware.rate_limiting import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.services import auth_service, websocket_service
from app.routers import document, chat
from app.utils.logging import setup_logging
import os
from contextlib import asynccontextmanager
from app.models.database import Base
from app.dependencies import engine

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the PostgreSQL Database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
    yield

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
