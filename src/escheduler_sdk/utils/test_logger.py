import logging
import os
import sys
from logging import FileHandler
from datetime import datetime

# Test logger configuration
TEST_LOG_DIR = 'logs'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'


def setup_test_logger(name='test-logger'):
    """
    Set up a logger for testing purposes.
    It logs to the console and a unique file for each run in the `logs/test` directory.
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(getattr(logging, LOG_LEVEL.upper()))
    logger_instance.propagate = False

    # Ensure the test log directory exists
    if not os.path.exists(TEST_LOG_DIR):
        os.makedirs(TEST_LOG_DIR)

    # Clear existing handlers to prevent duplicate logs
    if logger_instance.hasHandlers():
        logger_instance.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger_instance.addHandler(console_handler)

    # File handler for test logs - with timestamp to create a new file for each run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_filename = f"{name}-{timestamp}.log"
    file_handler = FileHandler(
        os.path.join(TEST_LOG_DIR, log_filename),
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger_instance.addHandler(file_handler)

    return logger_instance


# Initialize a default test logger instance
test_logger = setup_test_logger()


def log_test_exception(logger_instance=test_logger, exc_info=None):
    """
    Logs detailed exception information for tests.
    """
    logger_instance.error(
        'Exception occurred during test',
        exc_info=exc_info or sys.exc_info()
    )


__all__ = ['test_logger', 'log_test_exception', 'setup_test_logger']