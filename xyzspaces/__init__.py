# Copyright (C) 2019-2021 HERE Europe B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# License-Filename: LICENSE

"""The XYZ Spaces for Python - manage your XYZ Hub server or HERE Data Hub.

XYZ Spaces for Python allows you to manage XYZ spaces, projects and tokens with the Hub
API, Project API, and Token API, respectively. The Hub API provides the most
features to let you read and write GeoJSON data (features) from and to an
XYZ space, and perform some higher-level operations like return features
inside or clipped by some bounding box or map tile. The Project API and
Token API let you manage your XYZ projects and tokens.

See also:
- XYZ Hub server: https://github.com/heremaps/xyz-hub
- HERE Data Hub: https://developer.here.com/products/data-hub
"""

import os
from typing import Optional

from xyzspaces.__version__ import __version__  # noqa: F401
from xyzspaces.logconf import setup_logging  # noqa: F401
from xyzspaces.spaces import Space

from .apis import HubApi
from .constants import XYZ_BASE_URL


class XYZ:
    """A single interface to interact with your XYZ Hub server or HERE Data Hub."""

    def __init__(
        self, credentials: Optional[str] = None, server: str = XYZ_BASE_URL
    ):
        """Instantiate an XYZ object, optionally with access credentials
         and custom base URL.

        :param credentials: A string to serve as authentication
            (a bearer token). Will be looked up in environment variable
            ``XYZ_TOKEN`` if not provided.
        :param server: A string as base URL for Data Hub APIs. Required
            only if Data Hub APIs are self-hosted. For self-hosted Data
            Hub instances ``credentials`` is not required.
        """
        if credentials:
            os.environ["XYZ_TOKEN"] = str(credentials)
            self.hub_api = HubApi(credentials=credentials, server=server)
        else:
            self.hub_api = HubApi(server=server)
        self.spaces = Space(api=self.hub_api, server=server)
