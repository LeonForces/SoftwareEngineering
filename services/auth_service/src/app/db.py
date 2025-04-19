from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.settings import settings

DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:" + \
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:" + \
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Зависимости для получения сессии базы данных
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
