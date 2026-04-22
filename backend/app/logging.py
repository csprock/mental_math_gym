import logging
from logging.config import dictConfig


def setup_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)-8s %(name)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                },
            },
            "root": {"handlers": ["console"], "level": level},
            "loggers": {
                "uvicorn": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.error": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.access": {"handlers": ["console"], "level": level, "propagate": False},
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
