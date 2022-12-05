import logging
import sys
from logging import FileHandler, StreamHandler, Formatter

LOGGERS = {}

def obtain(name: str, handler_name=None, level=logging.DEBUG) -> logging.Logger:
    # Try to use existing logger from LOGGERS dict, otherwise instantiate new one
    if not LOGGERS.get(name):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if handler_name is not None:
            # Log to file specified in handler_name
            fh = FileHandler(handler_name)
            fh.setFormatter(Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s'))
            logger.addHandler(fh)
        # Also log to stdout (e.g. terminal)
        sh = StreamHandler(sys.stdout)
        sh.setFormatter(Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s'))
        logger.addHandler(sh)
        LOGGERS[name] = logger
    return LOGGERS[name]