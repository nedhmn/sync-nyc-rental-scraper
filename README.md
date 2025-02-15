# NYC Rental Scraper

A Python-based pipeline for extracting and analyzing NYC rental listings data from StreetEasy, using NYC's official building database as a source of addresses.

## Purpose

This project was originally created to check if buildings from NYC's Class B Multiple Dwellings list have active listings on StreetEasy. While the current implementation is specific to this use case, the architecture is modular:

- The `address_extractor.py` can be modified to ingest addresses from any source
- The core StreetEasy scraping and validation logic remains the same
- The pipeline confirms address matches to ensure accuracy

The main goal is to reliably determine if a given address has active listings on StreetEasy while handling anti-bot measures and rate limiting. This can be particularly useful for real estate analytics, market research, or monitoring specific buildings at small to medium scale.

## BrightData Web Unlocker API

This project utilizes BrightData's Web Unlocker API for reliable scraping. From the [official documentation](https://docs.brightdata.com/scraping-automation/web-unlocker/introduction):

### Overview

- Handles proxy and unblocking infrastructure automatically

### Key Features

- Intelligent proxy network selection
- Browser fingerprinting management
- CAPTCHA handling
- Real-user behavior emulation

## Features

- Extracts addresses from NYC government's Class B Multiple Dwellings database
- Scrapes corresponding rental listings from StreetEasy
- Handles rate limiting and anti-bot measures via BrightData's Web Unlocker
- Multi-threaded processing for improved performance
- Built-in error handling and retry mechanisms

## Prerequisites

- Python 3.12+ (if using Python)
- Docker Compose (if using Docker)
- BrightData account with Web Unlocker access

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/nyc-rental-scraper.git
cd nyc-rental-scraper
```

2. Create a `.env` file in the project root with your BrightData credentials:

```env
BRIGHTDATA_USERNAME=your_username
BRIGHTDATA_PASSWORD=your_password
BRIGHTDATA_HOST=your_host
```

3. Ensure the `compose.yml` file is present in the project root.

## Usage

Install packages and run script:

```bash
uv sync --frozen
uv run py -m scripts.nycrental_pipeline
```

or...

Build and run using Docker Compose:

```bash
docker compose build
docker compose up
```

Monitor the output and logs in the `data/run_[timestamp]` directory. Each run creates a new directory with a timestamp.

### Output Format

The pipeline generates a CSV file with the following columns:

- `address`: Original address from NYC government database
- `se_initial_url`: Generated StreetEasy search URL for the address
- `se_unit_name`: Name of the unit/building from StreetEasy listing (if available)
- `se_unit_address`: Address found on StreetEasy listing page (if available)
- `se_has_listing`: Boolean indicating if any active listings were found (uses PHRASE_LIST from config to detect "no results" pages)
- `same_address`: Boolean indicating if the cleaned NYC government address matches the cleaned StreetEasy address
- `status`: Status of the scraping attempt ('success' or 'failed')

To identify valid rental listings, look for rows where:

1. `status = 'success'` (successful scrape)
2. `same_address = True` (confirmed address match)

This two-step validation ensures that the StreetEasy listing corresponds to the correct building from the NYC database.

## Configuration

The pipeline uses Pydantic for configuration management. All settings are defined in `settings.py`:

### BrightData Configuration

- `BRIGHTDATA_HOST`: BrightData host URL (from .env)
- `BRIGHTDATA_USERNAME`: BrightData username (from .env)
- `BRIGHTDATA_PASSWORD`: BrightData password (from .env)
- `BRIGHTDATA_CERT_FILE`: Path to [BrightData certificate](https://docs.brightdata.com/general/account/ssl-certificate)

### URL Configuration

- `NYC_BASE_URL`: Base URL for NYC government site
- `NYC_SOURCE_URL`: URL for Class B Multiple Dwellings list
- `SE_BASE_URL`: StreetEasy search URL

### Pipeline Settings

- `BOROUGHS_TO_KEEP`: List of boroughs to include (default: `["MANHATTAN"]`)
- `MAX_WORKERS`: Number of concurrent threads (default: 30)
- `TIMEOUT`: Request timeout in seconds (default: 30)
- `PHRASE_LIST`: List of phrases indicating no listing found on StreetEasy

## Error Handling

### BrightData Performance

BrightData's Web Unlocker service has an observed success rate of around 70% for StreetEasy requests. You can:

- Monitor your success rate at [this link](https://docs.brightdata.com/scraping-automation/web-unlocker/features#get-success-rate-statistics-per-domain)
- Adjust the retry mechanism in `street_easy_transformer.py` if needed

### Safety Features

- Automatic retries for failed requests with static backoff
- Consecutive error detection (aborts after 10 consecutive failures)
