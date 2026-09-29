# from pathlib import Path
#
# from pydantic_settings import BaseSettings, SettingsConfigDict
# BASE_DIR: Path = Path(__file__).resolve().parent.parent
#
# class IMAPSettings(BaseSettings):
#     imap_host: str
#     imap_port: int = 993
#     imap_user: str
#     imap_password: str
#     imap_folder: str = "INBOX"
#
#     model_config = SettingsConfigDict(env_file=".env")
#
#
# imap_settings = IMAPSettings(env_file=".env")
#
