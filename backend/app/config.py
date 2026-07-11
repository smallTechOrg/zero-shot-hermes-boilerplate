from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "demo-agent"
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # LLM config. Set LLM_PROVIDER=gemini and GEMINI_API_KEY (or LLM_API_KEY)
    # to enable live responses. Empty key => [stub] mode.
    LLM_PROVIDER: str = "gemini"  # gemini | openai
    LLM_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    LLM_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    LLM_MODEL: str = "gemini-1.5-flash"

    @property
    def resolved_api_key(self) -> str | None:
        if self.LLM_API_KEY:
            return self.LLM_API_KEY
        if self.LLM_PROVIDER == "gemini" and self.GEMINI_API_KEY:
            return self.GEMINI_API_KEY
        return None

    @property
    def is_live(self) -> bool:
        return self.resolved_api_key is not None


settings = Settings()
