# -*- coding: utf-8 -*-

"""Tests for the logging module."""

import logging
import os
import unittest.mock

import pytest

from logginginitializer.logging_config import LoggingConfig
from logginginitializer.logging_initializer import LoggingInitializer


class TestLogging:
    """Test class for logging methods"""

    @staticmethod
    @unittest.mock.patch(
        "logginginitializer.logging_initializer.LoggingInitializer._define_log_directory"
    )
    @unittest.mock.patch(
        "logginginitializer.logging_initializer.LoggingInitializer._set_basicconfig"
    )
    def test_identifier_file(mock_basic, mock_log_directory, tmp_path):
        log_dir = "log_dir"
        with tmp_path as log_path:
            mock_log_directory.return_value = log_path
            identifier = "test"
            config = LoggingConfig(
                **{"identifier": identifier, "directory": log_dir},
            )
            logger = LoggingInitializer(config)
            assert logger.file == os.path.join(log_path, f"{identifier}.log")

    @pytest.mark.parametrize("quiet", [True, False])
    @unittest.mock.patch(
        "logginginitializer.logging_initializer.LoggingInitializer._define_log_directory"
    )
    def test_define_logging(self, mock_log_directory, tmp_path, caplog, quiet):
        log_dir = "log_dir"
        with tmp_path as log_path:
            mock_log_directory.return_value = log_path
            config = type(
                "LoggingConfig",
                (object,),
                {
                    "identifier": "test",
                    "directory": log_dir,
                    "log_level": None,
                    "log_format": None,
                    "date_format": None,
                    "backup_count": 50,
                },
            )

            logger = LoggingInitializer(config)
            logger._set_basicconfig()
            log = logging.getLogger(__name__)
            assert len(caplog.records) == 0
            log.critical("test")
            assert len(caplog.records) == 1
            logger._set_basicconfig(quiet=True)
            log = logging.getLogger(__name__)
            log.critical("test")
            assert len(caplog.records) == 2
            caplog.clear()

    @staticmethod
    @unittest.mock.patch("os.makedirs")
    @unittest.mock.patch(
        "logginginitializer.logging_initializer.LoggingInitializer._set_basicconfig"
    )
    def test_log_path(mock_basic, mock_makedirs):
        log_dir = "log_dir"
        logging_config = type(
            "LoggingConfig",
            (object,),
            {
                "identifier": "test",
                "directory": log_dir,
                "log_level": None,
                "log_format": None,
                "date_format": None,
            },
        )

        logger = LoggingInitializer(logging_config)
        expected_log_path = os.path.join(log_dir)
        assert os.path.dirname(logger.file) == expected_log_path

    def test_log_path_no_dir(self):
        config = LoggingConfig(identifier="test")
        LoggingInitializer(config)
        log = logging.getLogger(__name__)
        log.warning("test")

    def test_log_path_quiet_and_no_logdir(self):
        """Test whether ValueError is raised when no log directory and quiet is True.

        If you set quiet to True there will be no output to stdout.
        If you set no log directory there will be no output to file.
        E.g. if you set both quiet to True and define no log directory there will be no logging
        and a ValueError should be raised.
        """
        with pytest.raises(ValueError):
            config = LoggingConfig(identifier="test")
            LoggingInitializer(config, quiet=True)

    def test__define_log_directory(self):
        """Test whether ValueError is raised when no log directory is defined.

        If you call _define_log_directory without defining a log directory a ValueError should be
        raised.
        """
        with pytest.raises(ValueError):
            config = LoggingConfig(identifier="test")
            LoggingInitializer._define_log_directory(config)

    def test_log_only_stdout(self, caplog):
        """Test whether only stdout is logged when no log directory is defined.

        If you call _define_log_directory without defining a log directory a ValueError should be
        raised.
        """
        config = LoggingConfig(identifier="test")
        LoggingInitializer(config)
        log = logging.getLogger(__name__)
        log.warning("test")
        assert len(caplog.records) == 1
        assert caplog.records[0].message == "test"
        caplog.clear()
