from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str
    LLM_TIMEOUT_SEC: int = 60
    LLM_TIMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 900

settings = Settings()