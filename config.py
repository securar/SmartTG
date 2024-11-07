from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from smart_tg.modules import __all__ as modules

load_dotenv()

PREFIX = "-"
MODULES = [
    *modules,
]


class EnvSettings(BaseSettings):
    API_ID: str
    API_HASH: str

    model_config = SettingsConfigDict(env_file=".env")


env_settings = EnvSettings()
