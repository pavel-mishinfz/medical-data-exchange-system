from typing import Tuple, Type
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import PostgresDsn, Field, FilePath, SecretStr


class Config(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        default='postgresql://user:pass@localhost:5432/foobar',
        env='POSTGRES_DSN',
        alias='POSTGRES_DSN'
    )

    default_data_config_path: FilePath = Field(
        default='default-data.json',
        env='DEFAULT_DATA_CONFIG_PATH',
        alias='DEFAULT_DATA_CONFIG_PATH'
    )

    path_to_storage: str = Field(
        default='storage/',
        env='PATH_TO_STORAGE',
        alias='PATH_TO_STORAGE'
    )

    encrypt_key: SecretStr = Field(
        default='encrypt_key',
        env='ENCRYPT_KEY',
        alias='ENCRYPT_KEY'
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
