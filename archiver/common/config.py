#
# Configuration parser
#

import os
import yaml

from .errors import *

_singleton = None

class Configuration(object):
    """Class which represents the archiver configuration. The configuration
    is a YAML file."""

    def __init__(self, path):
        config_file = open(path, 'r')
        config = yaml.safe_load(config_file)
        self.__dict__.update(config)

    def validate(self):
        """Check whether the configuration makes sense."""

        supported_engines = ["mysql"]
        log_levels = ["debug", "info", "warning", "error", "critical"]

        for key, settings in self.databases.items():
            if settings["type"] not in supported_engines:
                raise ConfigError("Unsupported engine specified for database %s" % key)
            if "name" not in settings or "user" not in settings or "password" not in settings:
                raise ConfigError("The database must have name, user and password specified")

        if self.database["master"] not in self.databases:
            raise ConfigError("The master database parameters are not specified")

        if not all(slave in self.databases for slave in self.database["slaves"]):
            raise ConfigError("The slave database parameters are not specified")

        if self.log_level not in log_levels:
            raise ConfigError("Invalid log level specified: %s" % self.log_level)

        if not os.access(self.log_file, os.W_OK):
            raise ConfigError("The log file is not writeable")

def get():
    global _singleton
    return _singleton

def set(configuration):
    global _singleton
    _singleton = configuration

