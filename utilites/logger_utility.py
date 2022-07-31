import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    """Returns logging object that streams to file"""
    logger = logging.getLogger('tupilaqs')
    logger.setLevel(logging.DEBUG)

    log_file = 'tupilaqs.log'
    ch = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024,
                             backupCount=2, encoding=None, delay=False)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger
