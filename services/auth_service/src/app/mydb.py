from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = "postgres+asyncpg://admin:secret@localhost/db-users"
engine = create_async_engine(DATABASE_URL)


async def get_db():
    async with AsyncSession(engine) as session:
        yield session
