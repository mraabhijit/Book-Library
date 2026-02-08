from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


SQLALCHEMY_DATABASE_URL = settings.database_url


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # disable SQL query logging
    pool_pre_ping=True,  # ensure connections are alive before using
    pool_size=5,
    max_overflow=10,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
