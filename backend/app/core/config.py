from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SentiMind"

    HF_API_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    class Config:
        env_file = (".env", "../.env")
        extra = "ignore"


settings = Settings()
