from dataclasses import dataclass
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

@dataclass(frozen=True)
class Settings:
    api_url: str
    api_lang: str
    db_url: str
    news_category: list

def load_settings() -> Settings:
    api_url = os.getenv("API_URL")
    db_url = os.getenv("DB_URL")
    api_lang = os.getenv("API_LANG", "en")
    news_category = os.getenv("NEWS_CATEGORY", "").split(",")

    if not api_url:
        raise RuntimeError("API_URL not set")
    if not db_url:
        raise RuntimeError("DB_URL not set")

    return Settings(api_url=api_url, api_lang=api_lang, db_url=db_url, news_category=news_category)
