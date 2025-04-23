from sqlalchemy import select, insert, update, delete

from app.db import AsyncSessionLocal
from app.models import User


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with AsyncSessionLocal() as session:
            querry = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.mappings().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with AsyncSessionLocal() as session:
            querry = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.mappings().first()

    @classmethod
    async def add_(cls, **data):
        async with AsyncSessionLocal() as session:
            querry = insert(cls.model).values(**data)
            await session.execute(querry)
            await session.commit()

    @classmethod
    async def delete_(cls, **data):
        async with AsyncSessionLocal() as session:
            querry = delete(cls.model).filter_by(**data)
            await session.execute(querry)
            await session.commit()

    @classmethod
    async def update_(cls, model_id: int, **data):
        async with AsyncSessionLocal() as session:
            querry = update(cls.model).where(
                cls.model.id == model_id
            ).values(**data)
            await session.execute(querry)
            await session.commit()


class UserDAO(BaseDAO):
    model = User
