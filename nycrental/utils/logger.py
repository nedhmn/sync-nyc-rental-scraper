import logging
from pathlib import Path
from typing import Optional


def setup_logger(log_file: Optional[Path] = None, level: int = logging.INFO) -> None:
    """Configure root logger with console and optional file output"""
    handlers = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=handlers,
        force=True,
    )
