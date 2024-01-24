import logging
import datetime
import pathlib

from pathlib import Path


loggers = {}


def setup_custom_logger(name, log_level=logging.INFO):
    if loggers.get(name):
        return loggers[name]

    logger = logging.getLogger(name)
    loggers[name] = logger

    path = pathlib.Path(__file__).parent.resolve()

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(log_level)

    log = Path(f'{path}/../logs/{datetime.datetime.now()}.log')
    log.touch(exist_ok=True)

    fh = logging.FileHandler(log)
    fh.setFormatter(formatter)
    fh.setLevel(log_level)

    logger.addHandler(handler)
    logger.addHandler(fh)
    return logger
