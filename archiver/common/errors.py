class SetupError(Exception):
    """An error which occurred during the setup stages like configuration or
    connection to the database."""

    pass

class ConfigError(Exception):
    """An error caused by invalid configuration supplied."""

    pass

