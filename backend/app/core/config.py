from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GT_", extra="ignore")

    app_name: str = "Goal Tactics API"
    app_env: str = "dev"
    simulation_server_secret: str = "change-me-simulation-secret"
    auth_token_ttl_seconds: int = 3600
    state_dir: str = "/tmp/gt-state"

    @property
    def state_dir_path(self) -> Path:
        return Path(self.state_dir)


settings = Settings()
