# -*- coding: utf-8 -*-

"""
Process logging module.

Creates the log file and sets the logging format and handlers.
"""

import logging
import logging.handlers
import os
from typing import List, Optional

from logginginitializer.logging_config import LoggingConfig


class LoggingInitializer:  # pylint: disable=too-few-public-methods
    """Logging definition class."""

    def __init__(self, config: LoggingConfig, quiet: bool = False):
        self._config = config
        log_directory = self._config.directory
        if not log_directory and quiet:
            raise ValueError(
                "Having both no log directory and quiet mode results in no logging."
            )
        self._file: Optional[str] = self._define_filename() if log_directory else None
        self._set_basicconfig(quiet)

    @property
    def file(self) -> str | None:
        """Getter of file property.

        Get the log file that is used.

        Returns
        -------
        str
            File path of configuration file.
        """
        return self._file

    def _define_filename(self) -> str:
        """Define log filename.

        Define the log filename based on the config settings.
        The filename has the format "[identifier].log".

        Returns
        -------
        str
            Log filename.
        """
        log_directory = self._define_log_directory(self._config)
        return os.path.join(log_directory, f"{self._config.identifier}.log")

    @staticmethod
    def _define_log_directory(logging_config: LoggingConfig) -> str:
        """Create log directory.

        Defines log directory. Creates the directory if it does
        not yet exist. Location is taken from config.

        Returns
        -------
        str
            Full path to log directory.
        """
        logging_directory = logging_config.directory
        if not logging_directory:
            raise ValueError("No directory defined for logging.")

        log_path = os.path.join(logging_directory)
        os.makedirs(log_path, exist_ok=True)
        return log_path

    def _set_basicconfig(self, quiet: Optional[bool] = False) -> None:
        """Define logging format and handlers.

        Define output format logging and logging handlers.

        Parameters
        ----------
        quiet
            True if output to stdout should not be enabled.
        """
        log_filename = self._file
        handlers: List[logging.Handler] = []
        if log_filename:
            roll_needed = os.path.isfile(log_filename)
            file_handler = logging.handlers.RotatingFileHandler(
                log_filename, backupCount=self._config.backup_count
            )
            if roll_needed:
                file_handler.doRollover()
            handlers.append(file_handler)

        if not quiet:
            handlers.append(logging.StreamHandler())

        logging.basicConfig(
            level=self._config.log_level,
            format=self._config.log_format,
            datefmt=self._config.date_format,
            handlers=handlers,
        )
