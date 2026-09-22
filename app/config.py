"""Configuracion de la aplicacion leida desde variables de entorno."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./financial.db"
    secret_key: str = "cambiar-esta-clave-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
