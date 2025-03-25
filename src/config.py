from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Database env variables
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    # Redis env variables
    REDIS_HOST: str
    REDIS_PORT: int

    # fastapi app env variables
    APP_HOST: str
    APP_PORT: int

    # logging env variables
    LOGGING_LEVEL: str
    LOGGING_FORMAT: str

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(env_file=".env")
