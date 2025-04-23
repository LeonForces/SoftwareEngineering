from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)

    # __table_args__ = (
    #     Index('my_index', "email", postgresql_using="btree")
    # )
