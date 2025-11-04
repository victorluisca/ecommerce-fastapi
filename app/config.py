from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Commerce API"

    jwt_secret_key: str = "my_secret_key"
    jwt_expire_minutes: int = 10
    jwt_algorithm: str = "HS256"

    admin_full_name: str = "Admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "AdminPassword123!"

    stripe_secret_key: str = "sk_test..."
    stripe_webhook_secret: str | None = None

    database_url: str = "sqlite:///./ecommerce.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
