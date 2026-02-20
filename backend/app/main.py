from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pubsub import get_connection

from app.config import settings
from app.database import engine
from app.exceptions import (
    ActionForbiddenError,
    AlreadyExistsError,
    InvalidCredentialsError,
    LibraryException,
    NotFoundError,
)
from app.redis_client import close_redis, init_redis
from app.routers import auth, books, borrowings, members


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    Database schema is managed via Alembic migrations.
    """
    try:
        await init_redis()
    except Exception as e:
        print("WARNING :: Redis Unreachble: ", e)

    # RMQ
    try:
        rmq_conn = await get_connection(settings.rabbitmq_url)
        _app.state.rmq_channel = await rmq_conn.channel()
    except Exception as e:
        print("WARNING: RabbitMQ Unreachable: ", e)
        rmq_conn = None

    yield

    if rmq_conn:
        await rmq_conn.close()
    await close_redis()
    await engine.dispose()


# Initialize FastAPI application
app = FastAPI(
    title="Neighborhood Library API",
    description="API for managing library books, members, and borrowing operations",
    version="1.0.0",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app)

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(members.router, prefix="/api/members", tags=["members"])
app.include_router(borrowings.router, prefix="/api/borrowings", tags=["borrowings"])


@app.exception_handler(LibraryException)
async def library_exception_handler(request: Request, exc: LibraryException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, AlreadyExistsError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ActionForbiddenError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, InvalidCredentialsError):
        status_code = status.HTTP_401_UNAUTHORIZED

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint to verify API is running"""
    return {
        "message": "Welcome to Neighborhood Library API",
        "docs": "/docs",
    }
