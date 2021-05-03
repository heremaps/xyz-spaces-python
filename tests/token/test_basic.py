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

"""Module for testing HERE XYZ Token API endpoints."""

import datetime
import os

import pytest

from xyzspaces.apis import TokenApi
from xyzspaces.exceptions import ApiError

XYZ_TOKEN = os.environ.get("XYZ_TOKEN")


def test_get_invalid_token_raw(api):
    """Get response for an invalid token."""
    with pytest.raises(ApiError) as execinfo:
        api.get(path="/token-api/tokens/INVALID.json").text
    resp = execinfo.value.args[0]
    assert resp.status_code == 412
    assert resp.reason == "Precondition Failed"
    assert resp.text == "tokenId is not valid"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_token(api):
    """Get the token info."""
    info = api.get_token(XYZ_TOKEN)
    assert "description" in info
    assert "limits" in info
    assert "tid" in info


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_token_env_token(api):
    """Get the token info with default token directly from environment."""
    my_api = TokenApi()
    info = my_api.get_token(XYZ_TOKEN)
    assert "description" in info
    assert "limits" in info
    assert "tid" in info


# The following tests are considered "protected" and need access
# cookies which will be created when a TokenApi instance is created.

HERE_APP_ID = os.environ.get("HERE_APP_ID")
HERE_USER = os.environ.get("HERE_USER")
HERE_PASSWORD = os.environ.get("HERE_PASSWORD")


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD),
    reason="No HERE account credentials found.",
)
def test_get_tokens(api):
    """Get a list of tokens."""
    api.headers = {}
    tokens = api.get_tokens()
    assert type(tokens) == list
    exp = [
        "aid",
        "awsPlanId",
        "urm",
        "iat",
        "limits",
        "description",
        "cid",
        "tid",
    ]
    assert set(exp).issubset(set(tokens[0].keys()))


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD and HERE_APP_ID),
    reason="No HERE account credentials found.",
)
def test_create_token(api):
    """Create a new token."""
    utc_now = datetime.datetime.utcnow()
    # expiry data must be at least 60 minutes in the future
    expiry_date = utc_now + datetime.timedelta(minutes=90)
    data = dict(
        cid=HERE_APP_ID,
        exp=int(expiry_date.timestamp()),
        description=(
            "This is a disposable token for testing only "
            f"(expiring on {expiry_date} UTC)."
        ),
        urm={"xyz-hub": {"readFeatures": [{}]}},
        metadata=dict(foo=42),
    )
    info = api.post_token(json=data)
    assert info["description"] == data["description"]
    assert info["metadata"] == data["metadata"]


# This would need to remove the auth cookie for this to make sense...
def _test_delete_not_authorized_token(api):
    """Delete a token without authorization."""
    with pytest.raises(ApiError) as execinfo:
        api.delete_token("INVALID")
    resp = execinfo.value.args[0]
    assert resp.status_code == 401
    assert resp.reason == "Unauthorized"
    assert resp.json()["message"] == "Unauthorized"


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD),
    reason="No HERE account credentials found.",
)
def test_delete_non_existing_token(api):
    """Delete a non-existing token."""
    api.headers = {}
    with pytest.raises(ApiError) as execinfo:
        api.delete_token("INVALID")
    resp = execinfo.value.args[0]
    assert resp.status_code == 404
    assert resp.reason == "Not Found"
    assert resp.text == "Token not found"


@pytest.mark.skipif(
    not (HERE_USER and HERE_PASSWORD and HERE_APP_ID),
    reason="No HERE account credentials found.",
)
def test_delete_existing_token(api):
    """Delete an existing token."""
    # first create a token
    utc_now = datetime.datetime.utcnow()
    # expiry data must be at least 60 minutes in the future
    expiry_date = utc_now + datetime.timedelta(minutes=90)
    data = dict(
        cid=HERE_APP_ID,
        exp=int(expiry_date.timestamp()),
        description=(
            "This is a disposable token for testing only "
            f"(expiring on {expiry_date} UTC)."
        ),
        urm={"xyz-hub": {"readFeatures": [{}]}},
    )
    info = api.post_token(json=data)
    assert "token" in info
    token = info["token"]

    # delete it again
    info = api.delete_token(token)
    assert info == ""
