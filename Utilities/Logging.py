import logging
import os
import tempfile
from settings import LOGGING_TO_fILE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL


if LOGGING_TO_fILE:
    # Create a handler to record in file
    file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_logging.log')
    if os.path.exists(file_path):
        os.remove(file_path)
    logger_handler = logging.FileHandler(file_path)
else:
    # Create a handler to print data
    logger_handler = logging.StreamHandler()

# Create a Formatter to format log messages
logger_formatter = logging.Formatter("[%(asctime)s  %(levelname)s  %(filename) 17s.%(funcName)s() %(message)s")

# Add a Formatter to the handler
logger_handler.setFormatter(logger_formatter)

# Add a handler to Logger
logger.addHandler(logger_handler)

