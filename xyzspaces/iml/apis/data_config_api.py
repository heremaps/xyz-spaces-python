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
This module contains a :class:`DataConfigApi` class to perform API operations.

The HERE API reference documentation used in this module can be found here:
|config_api_reference|

.. |config_api_reference| raw:: html

   <a href="https://developer.here.com/documentation/data-api/api-reference-config.html" target="_blank">Config API Reference</a>  # noqa E501
"""
from typing import Any, Dict, Optional

from xyzspaces.iml.apis.api import Api
from xyzspaces.iml.auth import Auth


class DataConfigApi(Api):
    """This class defines data config APIs"""

    def __init__(
        self,
        auth: Auth,
        proxies: Optional[dict] = None,
    ):
        self.auth = auth
        super().__init__(
            access_token=auth.token,
            proxies=proxies,
        )
        self.base_url = "https://config.data.api.platform.here.com/config/v1"

    def create_catalog(  # type: ignore[return]
        self, data: Dict[str, Any], billing_tag: Optional[str] = None
    ) -> Dict:
        """
        Create a catalog.

        :param data: a dict with a catalog metadata.
        :param billing_tag: A string which is used for grouping billing records.
        :return: response from the API.
        """
        path = "/catalogs"
        url = "{}{}".format(self.base_url, path)
        params = {"billingTag": billing_tag} if billing_tag else {}
        resp = self.post(url, data, params)
        if resp.status_code == 202:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_catalog_status(  # type: ignore[return]
        self, catalog_status_href: str, billing_tag: Optional[str] = None
    ) -> tuple:
        """
        Get the status of the catalog operations for the given token.

        :param catalog_status_href: a catalog status href url.
        :param billing_tag: A string which is used for grouping billing records.
        :return: response from the API.
        """
        params = {"billingTag": billing_tag}
        resp = self.get(url=catalog_status_href, params=params)
        if resp.status_code in [200, 202, 303]:
            return resp.json(), resp.status_code != 202
        else:
            self.raise_response_exception(resp)

    def get_catalog_details(  # type: ignore[return]
        self, catalog_hrn: str, billing_tag: Optional[str] = None
    ) -> Dict:
        """
        Get the full catalog configuration for the requested catalog.

        :param catalog_hrn: a HERE Resource Name
        :param billing_tag: A string which is used for grouping billing records.
        :return: response from the API.
        """
        path = f"/catalogs/{catalog_hrn}"
        params = {"billingTag": billing_tag}
        url = "{}{}".format(self.base_url, path)
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def update_catalog(  # type: ignore[return]
        self, catalog_hrn: str, data: Dict[str, Any], billing_tag: Optional[str] = None
    ) -> dict:
        """
        Update a catalog.

        :param catalog_hrn: a HERE Resource Name.
        :param data: body of the update catalog request.
        :param billing_tag: A string which is used for grouping billing records.
        :return: a dict with catalog update status.
        """
        path = f"/catalogs/{catalog_hrn}"
        url = "{}{}".format(self.base_url, path)
        params = {"billingTag": billing_tag}
        resp = self.put(url=url, data=data, params=params)
        if resp.status_code == 202:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def delete_catalog(self, catalog_hrn: str, billing_tag: Optional[str] = None) -> dict:  # type: ignore[return] # noqa: E501
        """
        Delete a catalog.

        :param catalog_hrn: a HERE Resource Name.
        :param billing_tag: a string which is used for grouping billing records.
        :return: a dict with catalog deletion status.
        """
        path = f"/catalogs/{catalog_hrn}"
        url = "{}{}".format(self.base_url, path)
        params = {"billingTag": billing_tag}
        resp = self.delete(url, params)
        if resp.status_code == 202:
            return resp.json()
        else:
            self.raise_response_exception(resp)
