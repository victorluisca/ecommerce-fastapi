from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Commerce API"

    jwt_secret_key: str = "my_secret_key"
    jwt_expire_minutes: int = 10
    jwt_algorithm: str = "HS256"

    database_url: str = "sqlite:///./ecommerce.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
