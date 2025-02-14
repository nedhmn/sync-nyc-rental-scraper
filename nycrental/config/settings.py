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
    BOROUGHS_TO_KEEP: List = Field(["MANHATTAN"])
    NUM_THREADS: int = Field(10)
    TIMEOUT: int = Field(20)


settings = Settings()
