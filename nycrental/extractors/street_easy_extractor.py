import logging
import ssl
from typing import Tuple

import httpx
import pandas as pd
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from nycrental.config.settings import Settings

logger = logging.getLogger(__name__)


class StreetEasyExtractor:
    def __init__(self, settings: Settings):
        self.timeout = settings.TIMEOUT
        self.ctx = ssl.create_default_context(cafile=settings.BRIGHTDATA_CERT_FILE)
        self.proxy_url = httpx.HTTPTransport(
            proxy=(
                f"http://{settings.BRIGHTDATA_USERNAME}:"
                f"{settings.BRIGHTDATA_PASSWORD}@"
                f"{settings.BRIGHTDATA_HOST}"
            ),
            verify=self.ctx,
        )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(180),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.HTTPError, httpx.RemoteProtocolError)
        ),
        before_sleep=before_sleep_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
    )
    def fetch_listing(self, row: pd.Series) -> Tuple[pd.Series, str]:
        """Fetch listing data from StreetEasy URL"""
        with httpx.Client(
            mounts={"http://": self.proxy_url, "https://": self.proxy_url},
            timeout=self.timeout,
            follow_redirects=True,
            verify=self.ctx,
        ) as client:
            response = client.get(row["se_initial_url"])
            response.raise_for_status()

            # Add final URL after redirects to the row
            row["se_redirected_url"] = response.url

            return row, response.text
