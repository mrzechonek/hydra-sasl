from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    hydra_admin_url: str
    email_domain: str
    login_title: str
    login_bg_url: str = ""
    saslauthd_socket: str = "/var/run/saslauthd/mux"
    saslauthd_service: str = "login"


settings = Settings()
