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

"""
This module contains an :class:`LookupApi` class to perform API operations.

The HERE API reference documentation used in this module can be found here:
|lookup_api_reference|

.. |lookup_api_reference| raw:: html

   <a href="https://developer.here.com/documentation/api-lookup/api-reference-swagger.html">Lookup API Reference</a>  # noqa E501
"""

from typing import Optional

from xyzspaces.iml.apis.api import Api
from xyzspaces.iml.auth import Auth


class LookupApi(Api):
    """
    This class provides access to HERE platform Lookup APIs.

    Instances can call only to those API endpoints relevant for accessing
    catalog and layer metadata, as well as those needed to access the data
    contained in different types of layers.
    """

    api_version_impl = {
        "lookup": "v1",
        "interactive": "v1",
    }

    platform_api_version_impl = {"lookup": "v1", "config": "v1", "artifact": "v1"}

    def __init__(
        self,
        auth: Auth,
        proxies: Optional[dict] = None,
    ):
        super().__init__(
            access_token=auth.token,
            proxies=proxies,
        )
        server = "https://api-lookup.data.api.platform.here.com"
        base_path = "/lookup/" + self.api_version_impl["lookup"]
        self.base_url = f"{server}{base_path}"

    def get_resource_api_list(self, hrn: str, region: Optional[str] = None) -> dict:  # type: ignore[return]  # noqa E501
        """
        Lookup all available APIs for given HRN.

        :param hrn: a HERE Resource Name identifying the resource
        :param region: an Optional param to look up a specific region for a given resource
        :return: The list of APIs that can be used with the resource
        """
        path = f"/resources/{hrn}/apis"
        url = f"{self.base_url}{path}"
        params = dict(region=region)
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            apis: dict = {
                el["api"]: {k: v for (k, v) in el.items() if k != "api"}
                for el in resp.json()
                if el["api"] in self.api_version_impl
                and el["version"] == self.api_version_impl[el["api"]]
            }
            return apis
        else:
            self.raise_response_exception(resp)

    def get_resource_api(  # type: ignore[return]
        self, hrn: str, api: str, version: str, region: Optional[str] = None
    ) -> dict:
        """
        Return details of a single API for a given resource identified by hrn, api and
        version.

        :param hrn: a HERE Resource Name identifying the resource
        :param api: The identifier of the API
        :param version: The version of the API
        :param region: an Optional param to look up a specific region for a given resource
        :return: Details of the requested API for the resource
        """
        path = f"/resources/{hrn}/apis/{api}/{version}"
        url = f"{self.base_url}{path}"
        params = dict(region=region)
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()[0] if resp.json() else dict()
        else:
            self.raise_response_exception(resp)
