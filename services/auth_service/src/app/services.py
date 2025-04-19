from sqlalchemy import select, insert, update, delete

from app.db import Session
from app.models import User


class BaseDAO:
    model = None

    @classmethod
    def find_all(cls, **filter_by):
        with Session() as session:
            querry = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = session.execute(querry)
            return result.mappings().all()

    @classmethod
    def find_one_or_none(cls, **filter_by):
        with Session() as session:
            querry = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = session.execute(querry)
            return result.mappings().first()

    @classmethod
    def add_(cls, **data):
        with Session() as session:
            querry = insert(cls.model).values(**data)
            session.execute(querry)
            session.commit()

    @classmethod
    def delete_(cls, **data):
        with Session() as session:
            querry = delete(cls.model).filter_by(**data)
            session.execute(querry)
            session.commit()

    @classmethod
    def update_(cls, model_id: int, **data):
        with Session() as session:
            querry = update(cls.model).where(
                cls.model.id == model_id
            ).values(**data)
            session.execute(querry)
            session.commit()


class UserDAO(BaseDAO):
    model = User
