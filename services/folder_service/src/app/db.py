from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:" + \
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST_FOLDERS}:" + \
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB_FOLDERS}"
# DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:" + \
#     f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:" + \
#     f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)
# engine = create_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
# Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Зависимости для получения сессии базы данных
def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
