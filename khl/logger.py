import logging

KHL_LOGGER = logging.getLogger('khl')

KHL_LOGGER_HDLR = logging.StreamHandler()

KHL_LOGGER_FMT = logging.Formatter(
    f'[%(levelname)s] %(asctime)s @ %(name)s(%(funcName)s): %(message)s')

KHL_LOGGER_HDLR.setFormatter(KHL_LOGGER_FMT)
KHL_LOGGER_HDLR.setLevel(logging.DEBUG)
KHL_LOGGER.addHandler(KHL_LOGGER_HDLR)
KHL_LOGGER.setLevel(logging.INFO)


def enable_debug():
    KHL_LOGGER.setLevel(logging.DEBUG)


def disable_debug():
    KHL_LOGGER.setLevel(logging.INFO)
