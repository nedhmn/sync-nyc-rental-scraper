# NYC SRO Listings Scraper

A multi-threaded web scraper that tracks Single Room Occupancy (SRO) building availability in NYC by cross-referencing official NYC Housing Preservation & Development data with StreetEasy listings.

## Overview

This pipeline:

1. Extracts SRO building addresses from NYC government XLS files
2. Searches each address on StreetEasy using concurrent requests
3. Determines unit availability and building status
4. Outputs timestamped results to CSV for analysis

## Features

- Efficient multi-threaded processing
- Robust error handling with retry mechanisms
- Proxy support for reliable scraping
- Modular pipeline architecture
- Comprehensive logging
- CSV output with availability tracking
