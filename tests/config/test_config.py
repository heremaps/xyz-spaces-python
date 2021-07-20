"""This module tests custom configurations for xyzspaces."""

import os
from pathlib import Path

from xyzspaces.config.default import DEFAULT_CONFIG, XYZConfig


def test_default_config():
    """Test default config."""
    xyzconfig = XYZConfig.from_default()
    assert xyzconfig.config["credentials"]["XYZ_TOKEN"] == os.environ.get("XYZ_TOKEN")
    assert xyzconfig.config["credentials"]["HERE_USER"] == os.environ.get("HERE_USER")
    assert xyzconfig.config["credentials"]["HERE_PASSWORD"] == os.environ.get(
        "HERE_PASSWORD"
    )
    assert xyzconfig.config["url"] == "https://xyz.api.here.com"
    assert (
        xyzconfig.config["http_headers"]["Authorization"]
        == f"Bearer {os.environ.get('XYZ_TOKEN')}"
    )
    assert xyzconfig.config["http_headers"]["Content-Type"] == "application/geo+json"


def test_config_object():
    """Test configurations using config object."""
    xyzconfig = XYZConfig(**DEFAULT_CONFIG)
    assert xyzconfig.config["credentials"]["XYZ_TOKEN"] == os.environ.get("XYZ_TOKEN")
    assert xyzconfig.config["credentials"]["HERE_USER"] == os.environ.get("HERE_USER")
    assert xyzconfig.config["credentials"]["HERE_PASSWORD"] == os.environ.get(
        "HERE_PASSWORD"
    )
    assert xyzconfig.config["url"] == "https://xyz.api.here.com"
    assert (
        xyzconfig.config["http_headers"]["Authorization"]
        == f"Bearer {os.environ.get('XYZ_TOKEN')}"
    )
    assert xyzconfig.config["http_headers"]["Content-Type"] == "application/geo+json"


def test_config_from_file():
    """Test configurations using file."""
    root = Path(__file__).parent.parent.parent
    file_path = (
        root / Path("docs") / Path("notebooks") / Path("data") / "xyz_configuration.conf"
    )
    xyzconfig = XYZConfig.from_file(file_path)
    assert xyzconfig.config["credentials"]["XYZ_TOKEN"] == "MY-XYZ-TOKEN"
    assert xyzconfig.config["url"] == "https://xyz.api.here.com"
    assert xyzconfig.config["http_headers"]["Authorization"] == "Bearer MY-XYZ-TOKEN"
    assert xyzconfig.config["http_headers"]["Content-Type"] == "application/geo+json"
