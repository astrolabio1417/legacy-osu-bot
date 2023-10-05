import logging
import os
import sys
import time

# Create a logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

log_dir = os.path.join(os.getcwd(), "logs")

if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# Create a file handler and set the log file path
log_file_path = os.path.join(log_dir, f"logs-{time.strftime('%Y-%m-%d%H:%M:%S')}.log")
file_handler = logging.FileHandler(log_file_path)
stream_handler = logging.StreamHandler(sys.stdout)

# Create a formatter and set it for the file handler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
