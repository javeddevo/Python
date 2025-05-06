# logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file='app.log'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # File handler with rotation (5MB max per file, keep last 5 logs)
    file_handler = RotatingFileHandler(f'logs/{log_file}', maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
