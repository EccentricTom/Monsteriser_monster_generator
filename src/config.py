from dataclasses import dataclass
import os
from dotenv import load_dotenv, find_dotenv
import polars as pl
from pathlib import Path

load_dotenv(find_dotenv())

# @dataclass(frozen=True)
# class Settings:
#     api_url: str
#     api_lang: str
#     db_url: str
#     news_category: list

# def load_settings() -> Settings:
#     api_url = os.getenv("API_URL")
#     db_url = os.getenv("DB_URL")
#     api_lang = os.getenv("API_LANG", "en")
#     news_category = os.getenv("NEWS_CATEGORY", "").split(",")

#     if not api_url:
#         raise RuntimeError("API_URL not set")
#     if not db_url:
#         raise RuntimeError("DB_URL not set")

#     return Settings(api_url=api_url, api_lang=api_lang, db_url=db_url, news_category=news_category)

@dataclass(frozen=True)
class ChallengeRatingReference:
    reference: pl.DataFrame

    def get_reference_base(self) -> pl.DataFrame:
        return self.reference.drop(columns=["dpr_legend_min", "dpr_legend_max"])
    
    def get_references_legend(self) -> pl.DataFrame:
        return self.reference.select(["challenge_rating", "dpr_legend_min", "dpr_legend_max"])


def load_challenge_rating_reference() -> ChallengeRatingReference:
    df_filepath = Path("data/5E/baseline_stats.csv")
    df = pl.read_csv(df_filepath)
    return ChallengeRatingReference(reference=df)

@dataclass(frozen=True)
class GearReference:
    full_gear_reference: dict

    def get_melee_gear_reference(self) -> dict:
        return self.full_gear_reference.get("weapons").get("melee")
    
    def get_ranged_gear_reference(self) -> dict:
        return self.full_gear_reference.get("weapons").get("ranged")

def load_gear_reference() -> GearReference:
    filepath = Path("data/5E/gear.json")
    full_gear_reference = pl.read_json(filepath).to_dict(as_series=False)
    return GearReference(full_gear_reference=full_gear_reference)