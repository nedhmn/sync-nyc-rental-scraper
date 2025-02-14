import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import pandas as pd

from nycrental.config.settings import settings, Settings
from nycrental.extractors.address_extractor import AddressExtractor
from nycrental.extractors.street_easy_extractor import StreetEasyExtractor
from nycrental.utils.logger import setup_logger

setup_logger()
logger = logging.getLogger("scripts.nycrental_pipeline")


class PipelineOrchestrator:
    """Pipeline orchestrator for StreetEasy scraping process"""

    def __init__(self, settings: Settings):
        self.address_extractor = AddressExtractor(settings)
        self.street_easy_extractor = StreetEasyExtractor(settings)
        self.num_threads = settings.NUM_THREADS

    def _process_listing(self, row: pd.Series) -> Dict:
        """Process single listing with error handling"""
        try:
            row, html = self.street_easy_extractor.fetch_listing(row)
            print(row, html[:5])
            return html
        except Exception as e:
            logger.error(f"Error processing {row['address']}: {str(e)}")
            return None

    def run(self):
        """Execute the pipeline"""
        try:
            # Extract addresses
            logger.info("Starting address extraction...")
            addresses_df = self.address_extractor.fetch_addresses()

            # Process listings
            results = []
            logger.info("Starting listing extraction...")
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                future_to_row = {
                    executor.submit(self._process_listing, row): row
                    for _, row in addresses_df.head(5).iterrows()
                }

                for future in as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing {row['address']}: {str(e)}")

            # Load results
            logger.info("Pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


if __name__ == "__main__":
    pipeline = PipelineOrchestrator(settings)
    pipeline.run()
