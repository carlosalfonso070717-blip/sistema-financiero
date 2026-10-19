"""Configuracion de la aplicacion leida desde variables de entorno."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./financial.db"
    # Sin valor por defecto: el secreto se toma del ambiente (JWT_SECRET) o de .env.
    jwt_secret: str = ""
    access_token_expire_minutes: int = 30


settings = Settings()
