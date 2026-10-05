from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    azure_endpoint: str = ''
    azure_deployment: str = ''
    azure_api_key: str = ''
    max_turns: int = 40

