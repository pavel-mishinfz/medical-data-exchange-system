from typing import Tuple, Type
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import PostgresDsn, Field, SecretStr, HttpUrl


class Config(BaseSettings):
    postgres_dsn_async: PostgresDsn = Field(
        default='postgresql+asyncpg://user:pass@localhost:5432/foobar',
        env='POSTGRES_DSN_ASYNC',
        alias='POSTGRES_DSN_ASYNC'
    )

    CLIENT_ID: str = Field(
        default='client_id',
        env='CLIENT_ID',
        alias='CLIENT_ID'
    )

    ACCOUNT_ID: str = Field(
        default='account_id',
        env='ACCOUNT_ID',
        alias='ACCOUNT_ID'
    )

    CLIENT_SECRET: SecretStr = Field(
        default='client_secret',
        env='CLIENT_SECRET',
        alias='CLIENT_SECRET'
    )

    path_to_storage: str = Field(
        default='storage/',
        env='PATH_TO_STORAGE',
        alias='PATH_TO_STORAGE'
    )

    model_config = SettingsConfigDict(env_file=".env")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return dotenv_settings, env_settings, init_settings


def load_config() -> Config:
    return Config()
