from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Commerce API"
    database_url: str = "sqlite:///./ecommerce.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
