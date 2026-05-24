from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017/market_insights"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    GEMINI_API_KEY: str = ""
    GOOGLE_GENAI_USE_VERTEXAI: str = "FALSE"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
