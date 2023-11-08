from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field


class Config(BaseSettings):
    # TODO не работает PostgresDsn
    postgres_dsn: str = Field(
        default='postgresql://user:pass@localhost:5432/foobar',
        env='POSTGRES_DSN',
        alias='POSTGRES_DSN'
    )
    path_to_storage: str = Field(
        default='/src/storage/',
        env='PATH_TO_STORAGE',
        alias='PATH_TO_STORAGE'
    )

    model_config = SettingsConfigDict(env_file=".env")


def load_config() -> Config:
    return Config()
