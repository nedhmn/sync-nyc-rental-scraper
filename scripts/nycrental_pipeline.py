import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from nycrental.config.settings import Settings, settings
from nycrental.extractors.address_extractor import AddressExtractor
from nycrental.extractors.street_easy_extractor import StreetEasyExtractor
from nycrental.transfomers.street_easy_transformer import StreetEasyTransformer
from nycrental.utils.logger import setup_logger

setup_logger(Path(settings.OUTPUT_LOG_FILE))
logger = logging.getLogger("scripts.nycrental_pipeline")


class PipelineOrchestrator:
    """Pipeline orchestrator for StreetEasy scraping process"""

    def __init__(self, settings: Settings):
        self.address_extractor = AddressExtractor(settings)
        self.street_easy_extractor = StreetEasyExtractor(settings)
        self.street_easy_transformer = StreetEasyTransformer(settings)
        self.max_workers = settings.MAX_WORKERS
        self.output_csv_file = settings.OUTPUT_CSV_FILE

    def _process_listing(self, row: pd.Series) -> pd.Series:
        """Process single listing with error handling"""
        try:
            row, html = self.street_easy_extractor.fetch_listing(row)
            row = self.street_easy_transformer.transform_listing(row, html)

        except Exception as e:
            logger.error(f"Error processing {row['address']}: {str(e)}")
            row["status"] = "failed"

        row["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return row

    def run(self):
        """Execute the pipeline"""
        try:
            # Extract addresses
            logger.info("Starting address extraction...")
            addresses_df = self.address_extractor.fetch_addresses()

            # Process listings
            results = []
            consecutive_errors = 0
            logger.info("Starting listing extraction...")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_row = {
                    executor.submit(self._process_listing, row): row
                    for _, row in addresses_df.iterrows()
                }

                for future in as_completed(future_to_row):
                    row = future_to_row[future]
                    try:
                        results.append(future.result())
                        consecutive_errors = 0  # Reset counter on success

                    except Exception as e:
                        consecutive_errors += 1
                        logger.error(f"Error processing {row['address']}: {str(e)}")

                        if consecutive_errors >= 10:
                            # Cancel remaining tasks and exit
                            for f in future_to_row:
                                f.cancel()
                            logger.error("10 consecutive errors - aborting pipeline")
                            break

            # Load results
            results_df = pd.DataFrame(results)
            results_df.to_csv(self.output_csv_file, index=False)

            if consecutive_errors >= 10:
                raise RuntimeError("Aborted due to consecutive errors")

            logger.info("Pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


if __name__ == "__main__":
    pipeline = PipelineOrchestrator(settings)
    pipeline.run()
