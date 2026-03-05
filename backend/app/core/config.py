from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GT_", extra="ignore")

    app_name: str = "Goal Tactics API"
    app_env: str = "dev"
    simulation_server_secret: str = "change-me-simulation-secret"
    auth_token_ttl_seconds: int = 3600
    state_dir: str = "/tmp/gt-state"
    db_url: str = ""
    rate_limit_window_seconds: int = 60
    rate_limit_login_per_window: int = 30
    rate_limit_register_per_window: int = 20
    rate_limit_shop_grant_per_window: int = 60

    @property
    def state_dir_path(self) -> Path:
        return Path(self.state_dir)


settings = Settings()
