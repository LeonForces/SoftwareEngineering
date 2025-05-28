from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:" + \
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST_USERS}:" + \
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB_USERS}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
