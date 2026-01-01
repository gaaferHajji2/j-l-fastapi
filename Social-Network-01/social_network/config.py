from typing import Optional
from functools import lru_cache # This For Caching The Results Of Function
# Depending On Parameters
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(env_file='social_network/.env', extra="ignore")

class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    SECRET_KEY: str = "Test@123"
    ALGORITHM: str = "HS256"
    ACCESS_EXPIRE_MINUTES: int = 30
    CONFIRM_EXPIRE_MINUTES: int = 720
    API_KEY: str = ""
    HOST_NAME: str = ""
    API_TOKEN: str = ""
    API_URL: str = ""
    USERNAME: str = ""
    PASSWORD: str = ""
    EMAIL_HOST: str = ""
    EMAIL_PORT: str = ""
    B2_KEY_ID: Optional[str] = ""
    B2_APPLICATION_KEY: Optional[str] = ""
    B2_BUCKET_NAME: Optional[str] = ""

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='DEV_', extra="ignore")

class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='PROD_', extra="ignore")

class TestConfig(GlobalConfig):
    # In this way we override the values in .env-file
    # For test-State
    DATABASE_URL: Optional[str] = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True
    model_config = SettingsConfigDict(env_prefix='TEST_', extra="ignore")

@lru_cache()
def get_config(env_state: str) -> GlobalConfig:
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    if env_state.lower() not in configs.keys():
        raise Exception(f"Invalid value for env_state variable: {env_state}")
    
    return configs[env_state.lower()]()

config = get_config(BaseConfig().ENV_STATE)