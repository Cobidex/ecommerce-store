import logging
from datetime import datetime
import os


def get_logger(name):
    current_day = datetime.now().strftime('%Y-%m-%d')
    current_directory = os.getcwd()
    log_dir = f"{current_directory}/api/v1/logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(f"{log_dir}/{current_day}_{name}.log")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
