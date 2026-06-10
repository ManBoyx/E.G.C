"""Configuration centralisée du logging pour EGC Suite"""
import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure le logging avec le format standard EGC Suite."""
    logging.basicConfig(level=level, format=LOG_FORMAT)
