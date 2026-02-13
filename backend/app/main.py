from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import engine
from app.routers import auth, books, borrowings, members


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    Database schema is managed via Alembic migrations.
    """
    yield
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


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint to verify API is running"""
    return {
        "message": "Welcome to Neighborhood Library API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}
