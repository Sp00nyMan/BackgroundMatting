import logging
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)-8s] %(name)-10s : %(message)s")
# handler.setLevel(logging.NOTSET)
handler.setFormatter(formatter)

message_handler = logging.StreamHandler()
message_handler.terminator = ''
message_formatter = logging.Formatter("%(message)s")
message_handler.setFormatter(message_formatter)
message_handler.setLevel(logging.INFO)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(message_handler)
    return logger