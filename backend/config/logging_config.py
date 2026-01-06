import logging.config

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO"
    },
    "loggers": {
        "app": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
    }
}

def setup_logging():
    logging.config.dictConfig(logging_config)