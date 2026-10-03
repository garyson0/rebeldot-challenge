from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "localhost"
    postgres_port: int = 5433

    # LLM
    openai_api_key: SecretStr = SecretStr("")
    chat_model: str = "gpt-5.4-mini"
    router_model: str = "gpt-5.4-nano"
    embedding_model: str = "text-embedding-3-small"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2

    similarity_threshold: float = 0.7

    # API
    api_token: SecretStr = SecretStr("")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
