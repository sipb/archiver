from . import archive
from . import cas
from . import config
from . import database
from . import message

from .errors import *

import os as _os
import logging as _logging

def _setup_configuration(explicit_config_path):
    """Loads the configuration of the application."""

    default_config_path = "/etc/archiver.yaml"

    if explicit_config_path:
        config_path = explicit_config_path
    elif "ARCHIVER_CONFIG_PATH" in _os.environ:
        config_path = _os.environ["ARCHIVER_CONFIG_PATH"]
    elif _os.path.exists(default_config_path):
        config_path = default_config_path
    else:
        raise SetupError("Unable to establish the location of configuration file")

    global_config = config.Configuration(config_path)
    config.set(global_config)

def _setup_logging():
    log = _logging.getLogger('archiver')

    handler = _logging.FileHandler(config.get().log_file)
    log.addHandler(handler)

    formatter = _logging.Formatter(config.get().log_format)
    handler.setFormatter(formatter)

    log.setLevel(config.get().log_level.upper())

def setup(explicit_config_path = None):
    _setup_configuration(explicit_config_path)
    _setup_logging()

