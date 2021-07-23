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
"""This module defines Catalog class."""

from typing import Dict, Optional

from xyzspaces.iml.apis.aaa_oauth2_api import AAAOauth2Api
from xyzspaces.iml.apis.data_config_api import DataConfigApi
from xyzspaces.iml.apis.data_interactive_api import DataInteractiveApi
from xyzspaces.iml.apis.lookup_api import LookupApi
from xyzspaces.iml.auth import Auth
from xyzspaces.iml.credentials import Credentials


class Catalog:
    """A class to define catalog."""

    def __init__(
        self,
        hrn: str,
        credentials: Optional[Credentials] = None,
        proxies: Optional[dict] = None,
    ):
        self.hrn = hrn
        self.credentials = credentials or Credentials.from_default()
        self.proxies = proxies
        self.aaa_oauth2_api = AAAOauth2Api(
            base_url=self.credentials.cred_properties["endpoint"],
            proxies=proxies,
        )
        self.auth = Auth(self.credentials, aaa_oauth2_api=self.aaa_oauth2_api)
        self.lookup_api = LookupApi(
            auth=self.auth,
            proxies=self.proxies,
        )
        resource_apis = self.lookup_api.get_resource_api_list(hrn)
        self._data_interactive_api: DataInteractiveApi = DataInteractiveApi(
            base_url=resource_apis["interactive"]["baseURL"],
            auth=self.auth,
            proxies=proxies,
        )
        self._data_config_api = DataConfigApi(auth=self.auth, proxies=proxies)

    def get_details(self) -> Dict:
        """
        Get catalog details.
        :return: Dict
        """
        cat_config = self._data_config_api.get_catalog_details(catalog_hrn=self.hrn)
        return cat_config
