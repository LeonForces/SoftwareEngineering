from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    POSTGRES_HOST_USERS: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_USERS: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC: str

    class Config:
        env_file = ".env"


settings = Settings()
