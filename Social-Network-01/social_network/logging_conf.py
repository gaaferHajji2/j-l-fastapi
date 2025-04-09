import logging

from logging.config import dictConfig

from social_network.config import DevConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    characters = email[:obfuscated_length]

    first, last = email.split('@')

    return characters + ('*' * (len(first) - obfuscated_length)) + '@' + last

class EmailObfuscationFilter(logging.Filter):

    def __init__(self, name: str = "", obfuscated_length: int = 2):
        super().__init__(name)

        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:

        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)

        return True

def configure_logging() -> None:
    dictConfig({
        "version": 1, # This Is For Using Specific Version Of Logging
        # Until Now, It is The Only Version
        "disable_existing_loggers": False, 
        "filters": {
            "correlation_id": {
                # In This Way We Reject Any Logging Msg 
                # That Doesn't Contain CorrelationId-Value
                "()": "asgi_correlation_id.CorrelationIdFilter",
                # Here We Pass The Parameters To CorrelationIdFilter
                "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                "default_value": "-"
            },
            "email_obfuscation": {
                "()": EmailObfuscationFilter,
                "obfuscated_length": 2
            },
        },
        "formatters": {
            "console": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s"
            },

            "file": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                # "format": "%(asctime)s | %(levelname)-8s | (%(correlation_id)s) %(name)s:%(lineno)d - %(message)s"
                "format": "%(asctime)s %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s"
            },
        },
        "handlers": {
            "default": {
                "class": "rich.logging.RichHandler",
                "level": "DEBUG",
                "formatter": "console",
                "filters": ["correlation_id", "email_obfuscation"],
            },

            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": "j_l_social_network.log",
                "maxBytes": 1024 * 1024, # 1MB
                "backupCount": 2, # Only Save The Latest 2-Files Of Our Logs
                "encoding": "utf8",
                "filters": ["correlation_id","email_obfuscation"],
            },
        },
        "loggers": {
            "social_network": {
                "handlers": ["default", "rotating_file"],
                "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                "propagate": False, # This Will Prevent From Sending Logs To Parent
                # Note: The Main Parent For All Loggers Is Root
            },

            # In This Way We Override The Configuration Of 
            # uvicorn, databases, aiosqlite-Modules
            # Note: Not All Logs Will Be Formatted
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
