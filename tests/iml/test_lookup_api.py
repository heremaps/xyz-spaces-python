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
"""This module will test functionality of lookup_api."""

from xyzspaces.iml.apis.aaa_oauth2_api import AAAOauth2Api
from xyzspaces.iml.apis.lookup_api import LookupApi
from xyzspaces.iml.auth import Auth
from xyzspaces.iml.credentials import Credentials


def test_get_resource_api():
    """Test get resource api."""
    hrn = "hrn:here:data::olp-here:catalog-to-test-in-ci-don-not-delete"
    cred = Credentials.from_default()
    aaa_oauth2_api = AAAOauth2Api(base_url=cred.cred_properties["endpoint"], proxies={})
    auth = Auth(credentials=cred, aaa_oauth2_api=aaa_oauth2_api)
    lookup_api = LookupApi(auth=auth, proxies={})
    resource_apis = lookup_api.get_resource_api(hrn, api="interactive", version="v1")
    assert resource_apis == {
        "api": "interactive",
        "version": "v1",
        "baseURL": "https://interactive.data.api.platform.here.com/interactive/v1"
        "/catalogs/hrn:here:data::olp-here:catalog-to-test-in-ci-don-not"
        "-delete",
        "parameters": {},
    }
