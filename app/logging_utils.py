import logging
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)-8s] %(name)-10s : %(message)s")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger