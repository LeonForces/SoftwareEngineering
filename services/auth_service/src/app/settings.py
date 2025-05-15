from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_HOST_USERS: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_USERS: str

    REDIS_URL: str
    REDIS_HOST: str
    REDIS_PORT: str

    class Config:
        env_file = ".env"


settings = Settings()
