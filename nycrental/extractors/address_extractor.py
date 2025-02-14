import logging
import os
import tempfile
from urllib.parse import urlencode

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from nycrental.config.settings import Settings

logger = logging.getLogger(__name__)


class AddressExtractor:
    """Extracts rental listing addresses from NYC government website"""

    def __init__(self, settings: Settings):
        self.nyc_source_url = settings.NYC_SOURCE_URL
        self.nyc_base_url = settings.NYC_BASE_URL
        self.boroughs_to_keep = settings.BOROUGHS_TO_KEEP
        self.street_easy_base_url = settings.SE_BASE_URL

    def _normalize_url(self, href: str) -> str:
        """Ensure URL has proper format"""
        return href if href.startswith("http") else f"{self.nyc_base_url}{href}"

    def _get_xls_download_url(self, html_content: str) -> str:
        """Extract XLS download URL from HTML content"""
        soup = BeautifulSoup(html_content, "html.parser")
        p_tag = soup.find(
            "p",
            string=lambda text: "Class B Multiple Dwellings List (XLS)" in (text or ""),
        )

        if not p_tag:
            logger.error("XLS download paragraph not found")
            raise ValueError("Required content not found in page")

        a_tag = p_tag.find("a")
        if not a_tag or not a_tag.get("href"):
            logger.error("XLS download link not found")
            raise ValueError("Missing anchor tag in content")

        return self._normalize_url(a_tag["href"])

    def _create_street_easy_url(self, address: str) -> str:
        """Create StreetEasy search URL for address"""
        params = {"utf8": "✓", "search": address, "commit": ""}
        return f"{self.street_easy_base_url}?{urlencode(params)}"

    def _extract_addresses_from_xls(self, xls_content: bytes) -> pd.DataFrame:
        """Process XLS content and extract addresses with URLs"""
        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as tmp:
            tmp.write(xls_content)
            temp_path = tmp.name

        try:
            # Read and filter addresses
            addresses_df = (
                pd.read_excel(temp_path, skiprows=5)
                .query("Borough in @self.boroughs_to_keep")
                .assign(
                    se_initial_url=lambda df: df["Combined Address"].apply(
                        self._create_street_easy_url
                    )
                )
                .rename(columns={"Combined Address": "address"})
                .reset_index(drop=True)[["address", "se_initial_url"]]
            )

            logger.info(f"Found {len(addresses_df)} valid addresses")
            return addresses_df

        finally:
            os.unlink(temp_path)

    def fetch_addresses(self) -> pd.DataFrame:
        """Fetch and process addresses from source"""
        with httpx.Client() as client:
            # Get XLS URL
            response = client.get(self.nyc_source_url)
            response.raise_for_status()
            xls_url = self._get_xls_download_url(response.text)

            # Download and process XLS
            response = client.get(xls_url)
            response.raise_for_status()
            return self._extract_addresses_from_xls(response.content)
