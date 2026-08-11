"""
Local Logger.

Configures Python logging so the agent keeps its own on-disk logs
(e.g. `Agent Started`, `Configuration Loaded`, `Failed to Send Event`,
`Retry Successful`) while also mirroring to the console.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOGGER_NAME = "soc-agent"


class _CompactFormatter(logging.Formatter):
    """'timestamp LEVEL [module] message' one-line plain-text format."""

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        ts = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return (
            f"{ts} {record.levelname:<7} [{record.name}] "
            f"{record.module}:{record.funcName}: {record.message}"
        )


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    log_max_bytes: int = 5_000_000,
    log_backups: int = 3,
    quiet: bool = False,
) -> logging.Logger:
    """Configure the agent logger with a rotating file handler and console."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level.upper())
    logger.handlers.clear()
    logger.propagate = False

    formatter = _CompactFormatter()

    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(Path(log_dir) / "agent.log"),
            maxBytes=log_max_bytes,
            backupCount=log_backups,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger