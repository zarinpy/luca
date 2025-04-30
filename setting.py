from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    DB_URI: str


setting = Setting()
