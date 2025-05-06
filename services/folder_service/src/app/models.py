from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)

    # __table_args__ = (
    #     Index('my_index', "owner_id", postgresql_using="btree")
    # )
