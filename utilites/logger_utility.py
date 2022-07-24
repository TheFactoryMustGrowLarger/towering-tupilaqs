import logging


def setup_logger():
    """Returns logging object that streams to file"""
    logger = logging.getLogger('tupilaqs')
    logger.setLevel(logging.DEBUG)

    ch = logging.FileHandler('tupilaqs.log')
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger
