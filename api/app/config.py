from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: str
    database_url: str
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"


settings = Settings()
