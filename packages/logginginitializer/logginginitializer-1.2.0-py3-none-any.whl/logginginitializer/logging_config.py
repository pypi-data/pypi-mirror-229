# -*- coding: utf-8 -*-

"""
Configuration module for LoggingInitializer.

Stores and checks the configuration for the logger.
"""
import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class LoggingConfig(BaseModel):
    """
    Dataclass for the generic logging settings.

    Sets generic settings such as the base logging level, log directory and logging formats.
    """

    identifier: str
    directory: Optional[str] = None
    log_level: str = "INFO"
    log_format: str = "%(levelname)s:%(asctime)s - %(name)s - %(message)s"
    date_format: str = "%Y/%m/%d %H:%M:%S %p"
    backup_count: int = 50

    @field_validator("log_format")
    @classmethod
    def log_format_is_valid(cls, log_format: str) -> str:
        """Check whether the log format is acceptable for the logger.

        Parameters
        ----------
        log_format
            Log format string.

        Returns
        -------
        str
            Log format string.

        Raises
        ------
        ValidationError
            ValidationError is raised if invalid log format is supplied.
        """
        logging.Formatter(fmt=log_format)
        return log_format

    @field_validator("date_format")
    @classmethod
    def date_format_is_valid(cls, date_format: str) -> str:
        """Check whether the date format is acceptable for the logger.

        Parameters
        ----------
        date_format
            Date format string.

        Returns
        -------
        str
            Date format string.

        Raises
        ------
        ValidationError
            ValidationError is raised if invalid datetime format is supplied.
        """
        datetime.strptime(datetime.now().strftime(date_format), date_format)
        return date_format
