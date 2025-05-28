from sqlalchemy import insert
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.db import AsyncSessionLocal
from app.core import logger
from app.settings import settings
from app.models import User


class SUser(BaseModel):
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


async def add_to_db(data: dict):
    async with AsyncSessionLocal() as session:
        try:
            query = insert(User).values(**data)
            await session.execute(query)
            await session.commit()
            logger.info(f"User added: {data}")
        except Exception as e:
            await session.rollback()
            logger.error(f"DB error: {str(e)}")
            raise


async def read_kafka():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="my_group",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    await consumer.start()
    logger.info("Consumer started")

    while True:
        try:
            async for message in consumer:
                logger.debug(f"Received: {message.value}")

                # Проверяем тип данных
                if not isinstance(message.value, dict):
                    raise ValueError("Invalid message format")

                await add_to_db(message.value)
                await consumer.commit()
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
            await asyncio.sleep(5)
        finally:
            await consumer.stop()
            logger.info("Consumer stopped")


if __name__ == "__main__":
    try:
        asyncio.run(read_kafka())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
