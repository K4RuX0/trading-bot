import logging
import sys

def get_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(ch)
    logger.setLevel(level)
    return logger
