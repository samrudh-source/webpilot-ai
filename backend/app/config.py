from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./webpilot.db"
    gemini_api_key: str = ""
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
