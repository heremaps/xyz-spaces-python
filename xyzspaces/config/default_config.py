"""This module defines classes for default configuration for the project."""

import json
import os

# : This config dictionary is used by default to create object of XYZConfig class
# : if user does not provide config object for project level configurations.
DEFAULT_CONFIG = {
    "credentials": {
        "XYZ_TOKEN": os.environ.get("XYZ_TOKEN"),
        "HERE_USER": os.environ.get("HERE_USER"),
        "HERE_PASSWORD": os.environ.get("HERE_PASSWORD"),
    },
    "http_headers": {
        "Authorization": f"Bearer {os.environ.get('XYZ_TOKEN')}",
        "Content-Type": "application/geo+json",
    },
    "url": "https://xyz.api.here.com",
}


class XYZConfig:
    """This class defines methods to manage configurations for project."""

    def __init__(self, **kwargs):
        self.config = kwargs

    @classmethod
    def from_default(cls) -> "XYZConfig":
        """Return the default config for the project."""
        return cls(**DEFAULT_CONFIG)

    @classmethod
    def from_file(cls, path: str) -> "XYZConfig":
        """Return the config from file path provided."""
        with open(path) as fh:
            config_data = json.load(fh)
        return cls(**config_data)
