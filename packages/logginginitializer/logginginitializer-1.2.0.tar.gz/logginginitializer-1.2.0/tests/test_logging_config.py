"""Tests for the logging_config object."""
import pydantic
import pytest

from logginginitializer.logging_config import LoggingConfig


class TestLoggingConfig:
    """Test class for logging_config behaviour"""

    def test_empty_config(self):
        """Test whether an empty config raises an error."""
        config = {
            "identifier": None,
        }

        with pytest.raises(pydantic.ValidationError) as error:
            LoggingConfig(**config)

        # Retrieve the errors from the ValidationError object
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("identifier",)
        assert errors[0]["msg"] == "Input should be a valid string"

    def test_minimal_config(self):
        """Test whether a minimal config is accepted."""
        config = {"identifier": "test"}

        logging_config = LoggingConfig(**config)
        assert logging_config.log_level == "INFO"
        assert (
            logging_config.log_format
            == "%(levelname)s:%(asctime)s - %(name)s - %(message)s"
        )
        assert logging_config.date_format == "%Y/%m/%d %H:%M:%S %p"

    def test_log_level_config(self):
        """Test whether a log level config is set correctly."""
        config = {"identifier": "test", "log_level": "ERROR"}

        logging_config = LoggingConfig(**config)
        assert logging_config.log_level == "ERROR"

    def test_correct_log_format_config(self):
        """Test whether a log format config is set correctly."""
        config = {
            "identifier": "test",
            "log_format": "%(levelname)s:%(asctime)s - %(name)s - %(message)s",
        }

        logging_config = LoggingConfig(**config)
        assert (
            logging_config.log_format
            == "%(levelname)s:%(asctime)s - %(name)s - %(message)s"
        )

    def test_wrong_log_format_config(self):
        """Test whether an incorrect log format config raises an error."""
        config = {
            "identifier": "test",
            "log_level": "INFO",
            "log_format": "ERROR",
        }
        with pytest.raises(pydantic.ValidationError) as error:
            LoggingConfig(**config)

        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("log_format",)
        assert errors[0]["msg"] == "Value error, Invalid format 'ERROR' for '%' style"

    def test_wrong_date_format_config(self):
        """Test whether an incorrect date format config raises an error."""
        config = {"identifier": "test", "directory": "test", "date_format": "%^"}
        with pytest.raises(pydantic.ValidationError) as error:
            LoggingConfig(**config)

        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("date_format",)
        assert errors[0]["msg"] == "Value error, '%' is a bad directive in format '%^'"

    def test_correct_date_format_config(self):
        """Test whether a questionable date config is set correctly."""
        config = {"identifier": "test", "directory": "test", "date_format": "ERROR"}
        logging_config = LoggingConfig(**config)

        # this is a weird thing to use as a date format, but it's allowed
        assert logging_config.date_format == "ERROR"
