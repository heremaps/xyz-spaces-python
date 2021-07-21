"""This module defines ``IML`` class to interact with Interactive Map Layer."""

from typing import Optional

from xyzspaces.iml.credentials import Credentials


class IML:
    def __init__(self, credentials: Optional[Credentials] = None):
        self.credentials = credentials or Credentials.from_default()
        self.layer = ""
