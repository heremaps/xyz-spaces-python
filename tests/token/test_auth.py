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

"""Module for testing obtaining cookies to authenticate certain API endpoints."""

import os

import pytest

from xyzspaces.auth import get_auth_cookies
from xyzspaces.exceptions import AuthenticationError

HERE_USER = os.environ.get("HERE_USER")
HERE_PASSWORD = os.environ.get("HERE_PASSWORD")


def test_bad_credentials():
    """Raise error for invalid account credentials."""
    with pytest.raises(AuthenticationError):
        get_auth_cookies(username="foo", password="bar")


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD),
    reason="No HERE account credentials found.",
)
def test_get_access_cookie():
    """Get response for a valid cookie."""
    cookies = get_auth_cookies(HERE_USER, HERE_PASSWORD)
    exp = [
        "here_access_oidc",
        "here_auth_oidc",
        "here_access",
        "here_auth",
        "here_ca_access",
    ]
    assert set(cookies.keys()) == set(exp)


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD),
    reason="No HERE account credentials found.",
)
def test_get_tokens_cookies(api):
    """Get the tokens."""
    # url = "http://xyz.api.here.com/token-api/tokens"
    cookies = get_auth_cookies(HERE_USER, HERE_PASSWORD)
    # tokens = requests.get(url, cookies=cookies).json()
    api.headers = {}
    tokens = api.get(path="/token-api/tokens", cookies=cookies).json()
    assert type(tokens) == list

    api.headers = {}
    tokens = api.get(path="/token-api/tokens").json()
    assert type(tokens) == list

    api.headers = {}
    tokens = api.get_tokens()
    assert type(tokens) == list
