from datetime import datetime
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
RUN_DIR = f"data/run_{TIMESTAMP}"


class Settings(BaseModel):
    OUTPUT_CSV_FILE: str = Field(f"{RUN_DIR}/results.csv")
    OUTPUT_LOG_FILE: str = Field(f"{RUN_DIR}/logs.log")
    BRIGHTDATA_HOST: str = Field(os.getenv("BRIGHTDATA_HOST"))
    BRIGHTDATA_USERNAME: str = Field(os.getenv("BRIGHTDATA_USERNAME"))
    BRIGHTDATA_PASSWORD: str = Field(os.getenv("BRIGHTDATA_PASSWORD"))
    BRIGHTDATA_CERT_FILE: str = Field("nycrental/config/brightdata/cert.crt")
    NYC_BASE_URL: str = Field("https://www.nyc.gov")
    NYC_SOURCE_URL: str = Field(
        "https://www.nyc.gov/site/specialenforcement/reporting-law/class-b-mdl.page"
    )
    SE_BASE_URL: str = Field("https://streeteasy.com/search")
    BOROUGHS_TO_KEEP: List = Field(
        ["MANHATTAN"], description="Keep addresses that are in these borough(s)"
    )
    MAX_WORKERS: int = Field(30)
    TIMEOUT: int = Field(30)
    PHRASE_LIST: List = Field(
        [
            "no results found",
            "we couldn't find any matches",
            "try searching in a different area",
            "there were no matches for",
        ],
        description="When scraping an address from street-easy, if a page says any of these then there were no results.",
    )


settings = Settings()
