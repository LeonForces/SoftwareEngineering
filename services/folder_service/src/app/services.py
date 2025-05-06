from sqlalchemy import select, insert, update, delete
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from app.db import AsyncSessionLocal
from app.models import Folder
from app.settings import settings


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with AsyncSessionLocal() as session:
            querry = select(cls.model.__table__.columns)\
                .filter_by(**filter_by).limit(20)
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


class FolderDAO(BaseDAO):
    model = Folder


# Зависимости для получения текущего пользователя
async def get_user_id(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token missing"
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        else:
            return int(user_id)
    except JWTError:
        raise credentials_exception
