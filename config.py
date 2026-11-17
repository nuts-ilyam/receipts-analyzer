from typing import ContextManager
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

ENV_PATH = Path(__file__).resolve().parent / ".env"

class DatabaseSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def     database_url(self):
        return (
            f"postgresql+psycopg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/"
            f"{self.db_name}"
        )

    # class Config:
    #     env_file = ".env"


class IMAPSettings(BaseSettings):
    imap_host: str
    imap_port: int = 993
    imap_user: str
    imap_password: str
    imap_folder: str = "INBOX"

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

class LLMSettings(BaseSettings):
    llm_api_key: str
    llm_base_url: str
    llm_model_name: str
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


class Settings:
    db = DatabaseSettings()
    mail = IMAPSettings()
    llm = LLMSettings()

settings = Settings()

engine = create_engine(settings.db.database_url)

SessionLocal = sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@contextmanager
def db_session() -> ContextManager[Session]:
    """Wrapper for enabling IDE autocompletion."""
    return get_db()
