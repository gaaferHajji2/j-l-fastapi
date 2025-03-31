from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env', extra="ignore")

class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='DEV_')

class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='PROD_')

class TestConfig(GlobalConfig):
    # If We Want To Override These Variables We Can Add Them 
    # To .env-File
    DATABASE_URL: Optional[str] = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(env_prefix='TEST_')
