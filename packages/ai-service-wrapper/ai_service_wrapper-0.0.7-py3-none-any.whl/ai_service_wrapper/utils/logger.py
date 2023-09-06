import logging
import os
import sys
import json
from logging.config import dictConfig
import os.path as osp


def setup_logger(name, save_dir=None):
    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[PID %(process)d] %(asctime)s - %(name)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # if save_dir:
    #     if not osp.exists(save_dir):
    #         os.makedirs(save_dir)
    #         fh = logging.FileHandler(os.path.join(save_dir, "art_style_log.txt"), mode='w')
    #
    #     fh.setLevel(logging.DEBUG)
    #     fh.setFormatter(formatter)
    #     logger.addHandler(fh)

    return logger


def setup_logging_stream(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            dictConfig(config)
    else:
        logging.basicConfig(level=default_level)