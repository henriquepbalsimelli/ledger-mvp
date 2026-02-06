import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

settings = get_settings()

LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s " "%(request_id)s %(operation)s %(account_id)s %(asset)s"
    )

    handler.setFormatter(formatter)

    logger.handlers = []
    logger.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
