import logging
import sys
from .config import LOG_LEVEL

def setup_logging():
    """
    Configure logging for the application.

    Sets up both console and file logging with appropriate formatting.
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Clear any existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # File handler
    file_handler = logging.FileHandler('/tmp/wind_alert.log')
    file_handler.setLevel(numeric_level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger