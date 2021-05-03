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

"""Module for testing API exceptions."""


import pytest
import requests

from xyzspaces.exceptions import ApiError


def test_exception_requests_inalid(api):
    """Raise exception via requests as response for invalid endpoint."""
    with pytest.raises(ApiError) as execinfo:
        url = f"{api.xyzconfig.config['url']}/hub/invalid"
        resp = requests.get(url)
        raise ApiError(resp)
    resp = execinfo.value.args[0]
    assert resp.status_code == 404
    assert resp.reason == "Not Found"


def test_exception_requests_inalid_str(api):
    """Test raised exception as string follow expected pattern."""
    with pytest.raises(ApiError) as execinfo:
        url = f"{api.xyzconfig.config['url']}/hub/invalid"
        resp = requests.get(url)
        raise ApiError(resp)
    assert str(execinfo.value).startswith('404, Not Found, {"type":"error",')


def test_exception_response_invalid(api):
    """Raise exception via API as response for invalid endpoint."""
    with pytest.raises(ApiError) as execinfo:
        api.get(path="/hub/invalid")
    resp = execinfo.value.args[0]
    assert resp.status_code == 404
    assert resp.reason == "Not Found"
    assert resp.json()["message"] == "The requested resource does not exist."
