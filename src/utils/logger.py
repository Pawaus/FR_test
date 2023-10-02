import logging
import sys

logger_main = logging.getLogger("newsletter_logger")
logger_main.setLevel(logging.INFO)
handler_logger = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '{"asctime":"%(asctime)s","name":"%(name)s","levelname":"%(levelname)s","filename":"%(filename)s","funcName":"%('
    'funcName)s","process":"%(process)d","processName":"%(processName)s","thread":"%(thread)d","threadName":"%('
    'threadName)s","message":"%(message)s"}')

handler_logger.setFormatter(formatter)
logger_main.addHandler(handler_logger)