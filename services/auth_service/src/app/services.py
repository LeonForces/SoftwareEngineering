from sqlalchemy import select, insert, update, delete
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from typing import Optional
from aiokafka import AIOKafkaProducer
import json

from app.db import AsyncSessionLocal
from app.models import User
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


class UserDAO(BaseDAO):
    model = User


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


# Создание и проверка JWT токенов
async def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_kafka_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
