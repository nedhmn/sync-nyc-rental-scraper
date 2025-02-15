import logging
import re
from typing import Optional, Tuple

import bs4
import pandas as pd

from nycrental.config.settings import Settings

logger = logging.getLogger(__name__)


class StreetEasyTransformer:
    """Transforms raw HTML from StreetEasy into structured data"""

    def __init__(self, settings: Settings):
        self.phrase_list = settings.PHRASE_LIST

    @staticmethod
    def _extract_building_info(
        soup: bs4.BeautifulSoup,
    ) -> Tuple[str, str]:
        """Extract building name and address from HTML"""
        try:
            building_summary = soup.find(
                "section", attrs={"data-testid": "building-summary-component"}
            )

            if not building_summary:
                logger.debug("No building summary found in HTML")
                return None, None

            h1_tag = building_summary.find("h1")
            h2_tag = building_summary.find("h2")

            return (
                h1_tag.get_text(strip=True) if h1_tag else None,
                h2_tag.get_text(strip=True) if h2_tag else None,
            )

        except Exception as e:
            logger.error(f"Error extracting building info: {str(e)}")
            raise

    def _has_listing(self, html_content: str) -> bool:
        """Check if any phrase exists in content that indicates no listings"""
        try:
            content = html_content.lower()
            return not any(phrase.lower() in content for phrase in self.phrase_list)

        except Exception as e:
            logger.error(f"Error checking listing existence: {str(e)}")
            raise

    @staticmethod
    def _clean_address(address: str) -> Optional[str]:
        if not address:
            return None

        # Remove special characters and extra whitespace
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", address)

        # Convert to lowercase and remove extra spaces
        return " ".join(cleaned.lower().strip().split())

    def _compare_addresses(self, original_address: str, scraped_address: str) -> bool:
        """Compare two addresses after cleaning"""
        cleaned_original_address = self._clean_address(original_address)
        cleaned_scraped_address = self._clean_address(scraped_address)

        # Compare addresses
        return cleaned_original_address == cleaned_scraped_address

    def transform_listing(self, row: pd.Series, html_content: str) -> pd.Series:
        """Transform raw HTML into structured data"""
        try:
            # Parse once at the start
            soup = bs4.BeautifulSoup(html_content, "html.parser")

            # Use the same soup instance for all extractions
            unit_name, unit_address = self._extract_building_info(soup)
            has_listing = self._has_listing(html_content)
            same_address = (
                self._compare_addresses(row["address"], unit_address)
                if unit_address
                else None
            )

            row["se_unit_name"] = unit_name
            row["se_unit_address"] = unit_address
            row["se_has_listing"] = has_listing
            row["same_address"] = same_address
            row["status"] = "success"

            logger.debug(
                f"Transformed data for {row['address']}: se_has_listing={row['se_has_listing']}, "
            )

            return row

        except Exception as e:
            logger.error(f"Error transforming listing for {row['address']}: {str(e)}")
            raise
