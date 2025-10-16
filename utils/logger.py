import logging

def get_logger(name="AutoTraderPro"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
