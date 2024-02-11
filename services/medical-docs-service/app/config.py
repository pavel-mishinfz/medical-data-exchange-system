from typing import Tuple, Type
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import PostgresDsn, Field


class Config(BaseSettings): 
    postgres_dsn: PostgresDsn = Field(
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
