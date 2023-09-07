# Copyright(C) 2023 Anders Logg
# Licensed under the MIT License

import logging as _logging

def _init_logging(name):
    "Internal function for initializing logging"
    format = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
    _logging.basicConfig(format=format)
    logger = _logging.getLogger(name)
    logger.setLevel(_logging.INFO)    
    return (logger.debug,
            logger.info,
            logger.warning,
            logger.error,
            logger.critical)

debug, info, warning, error, critical = _init_logging("dtcc-common")

def init_logging(name):
    "Initialize logging for given package"    
    debug(f"Initializing logging for {name}")
    return _init_logging(name)

def set_log_level(level):
    """Set log level. Valid levels are:

    "DEBUG"
    "INFO"
    "WARNING"
    "ERROR"
    "CRITICAL"

    """
    logger.setLevel(level)
