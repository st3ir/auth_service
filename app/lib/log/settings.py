from pydantic import Field
from pydantic_settings import BaseSettings

from lib.log.formatter import CustomColorFormatter, CustomJsonFormatter
from lib.log.types import LogFormatterType, LogHandlerType


class LogSettings(BaseSettings):

    LOG_LEVEL: str | None = Field(
        "INFO",
        alias="LOG_LEVEL"
    )
    LOG_FORMATTER: LogFormatterType | None = Field(
        LogFormatterType.COLORED_STR,
        alias="LOG_FORMATTER"
    )
    LOG_HANDLERS: list[LogHandlerType] | None = Field(
        [LogHandlerType.STDOUT],
    )
    LOG_APP_NAME: str | None = Field(
        "AUTH",
        alias="LOG_APP_NAME"
    )

    _FMT: str | None = "%(asctime)s [%(levelname)s]|[{}]|[%(name)s]: %(message)s"
    _DATEFMT: str | None = "%Y-%m-%d %H:%M:%S"

    @property
    def main_conf(self) -> dict[str, dict | int]:

        fmt = self._FMT.format(self.LOG_APP_NAME)

        return {
            "version": 1,
            "formatters": {
                LogFormatterType.COLORED_STR: {
                    "()": lambda: CustomColorFormatter(
                        fmt=fmt,
                        datefmt=self._DATEFMT
                    ),
                },
                LogFormatterType.JSON: {
                    "()": lambda: CustomJsonFormatter(
                        fmt=fmt,
                        datefmt=self._DATEFMT,
                        static_fields={"app_name": self.LOG_APP_NAME},
                    ),
                }
            },
            "handlers": {
                LogHandlerType.STDOUT: {
                    "level": self.LOG_LEVEL,
                    "formatter": self.LOG_FORMATTER,
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {},
        }

    @property
    def default_loggers_conf(self) -> dict:

        return {
            "handlers": self.LOG_HANDLERS,
            "level": self.LOG_LEVEL,
            "propagate": False,
        }

    @property
    def app_loggers_conf(self) -> dict:

        return {
            "loggers": {
                "api": {**self.default_loggers_conf},
                "service": {**self.default_loggers_conf},
                "lib": {**self.default_loggers_conf},
                "db": {**self.default_loggers_conf},
                "uvicorn": {**self.default_loggers_conf},
                "boto3": {**self.default_loggers_conf},
            },
        }

    @property
    def sqlalchemy_loggers_conf(self) -> dict:

        return {
            "loggers": {
                "sqlalchemy": {**self.default_loggers_conf},
            }
        }

    def build(self) -> dict:

        return self.merge(
            self.main_conf,
            [
                self.app_loggers_conf,
                self.sqlalchemy_loggers_conf
            ]
        )

    @staticmethod
    def merge(main: dict, another_confs: list[dict]) -> dict:

        for conf in another_confs:
            main["loggers"].update(conf.get("loggers", {}))
            main["handlers"].update(conf.get("handlers", {}))
            main["formatters"].update(conf.get("formatters", {}))

        return main
