from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GT_", extra="ignore")

    app_name: str = "Goal Tactics API"
    app_env: str = "dev"


settings = Settings()
