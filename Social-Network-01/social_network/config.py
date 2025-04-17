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
    
    EXPIRE_MINUTES: int = 30

    API_KEY: str = ""

    HOST_NAME: str = ""

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='DEV_')

class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix='PROD_')

class TestConfig(GlobalConfig):
    # In This Way We Override The Values In .env-File
    # For test-State
    DATABASE_URL: Optional[str] = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(env_prefix='TEST_')

@lru_cache()
def get_config(env_state: str) -> GlobalConfig:
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}

    if env_state not in configs.keys():
        raise Exception(f"Invalid Value For env_state Variable {env_state}")
    
    return configs[env_state]()

config = get_config(BaseConfig().ENV_STATE)