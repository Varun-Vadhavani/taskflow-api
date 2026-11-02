import logging


def setup_logging(level: str) -> None:
    """Configure the root logger once at startup."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )