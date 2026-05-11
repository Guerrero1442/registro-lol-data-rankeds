# src/config/settings.py
from pydantic import FilePath
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str
    spreadsheet_id: str
    sheet_name: str
    game_name: str
    tag_line: str
    region_route: str = "americas"
    credentials_file: FilePath = "credentials.json"
    
    class Config:
        env_file = ".env"

settings = Settings()