from logging.config import dictConfig

from social_network.config import DevConfig, config

def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "%(name)s:%(lineno)d - %(message)s"
            },

            "file": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
            },
        },
        "handlers": {
            "default": {
                "class": "rich.logging.RichHandler",
                "level": "DEBUG",
                "formatter": "console",
            },

            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": "j_l_social_network.log",
                "maxBytes": 1024 * 1024, # 1MB
                "backupCount": 2,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "social_network": {
                "handlers": ["default", "rotating_file"],
                "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                "propagate": False,
            },

            "uvicorn": {
                "handlers": ["default", "rotating_file"],
                "level": "INFO",
            },

            "databases": {
                "handlers": ["default", "rotating_file"],
                "level": "INFO",
            },

            "aiosqlite": {
                "handlers": ["default", "rotating_file"],
                "level": "INFO",
            },
        },
    })
