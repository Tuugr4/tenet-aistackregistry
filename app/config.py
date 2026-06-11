from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://aibom:aibom@localhost:5434/aibom"

    model_config = {"env_file": ".env"}


settings = Settings()
