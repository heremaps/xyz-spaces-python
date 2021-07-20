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

"""Module for testing various endpoints of the XYZ API class."""

import random

import backoff
import pytest
import requests

# from fixtures import api, space_id  # noqa
from xyzspaces.apis import HubApi
from xyzspaces.datasets import get_countries_data
from xyzspaces.exceptions import TooManyRequestsException
from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()
gj_countries = get_countries_data()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_hub_info(api):
    """Get the hub info."""
    hub = api.get_hub()
    assert "reporter" in hub
    assert "status" in hub
    assert "schemaVersion" in hub
    hub = api.get_hub(params={})
    assert "reporter" in hub
    assert "status" in hub
    assert "schemaVersion" in hub


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_statistics(api, space_id):
    """Get space statistics."""
    stats = api.get_space_statistics(space_id=space_id)
    assert stats["type"] == "StatisticsResponse"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_statistics_env_token(space_id):
    """Get space statistics with default token directly from environment."""
    my_api = HubApi()
    stats = my_api.get_space_statistics(space_id=space_id)
    assert stats["type"] == "StatisticsResponse"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_count(api, space_id):
    """Get space count."""
    stats = api.get_space_count(space_id=space_id)
    assert stats["type"] == "CountResponse"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_patch_space(api, space_id):
    """Patch space."""
    data = {
        "title": "New Title",
        "description": "New Description",
        "license": "Apache-2.0",
    }
    res = api.patch_space(space_id=space_id, data=data)
    assert res["title"] == data["title"]
    assert res["license"] == data["license"]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_round_trip(api):
    """Put and delete a feature."""
    # create space
    res = api.post_space(
        data={"title": "Testing xyzspaces", "description": "Temporary space."}
    )
    space_id = res["id"]

    # add features
    api.put_space_features(
        space_id=space_id,
        data=gj_countries,
        add_tags=["foo", "bar"],
        remove_tags=["bar"],
    )

    # get one feature
    api.get_space_feature(space_id=space_id, feature_id="FRA")

    # delete space
    api.delete_space(space_id=space_id)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_round_trip1(api):
    """Put and delete a feature with a tag."""
    # create space
    res = api.post_space(
        data={
            "title": "Testing xyzspaces",
            "description": "Temporary space.",
        }
    )
    space_id = res["id"]

    # add features
    api.put_space_features(space_id=space_id, data=gj_countries, add_tags=["foo", "bar"])

    # delete one features with given tag
    res = api.delete_space_features(space_id=space_id, tags=["foo"])
    assert res == ""

    # delete space
    api.delete_space(space_id=space_id)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_round_trip2(api, space_id):
    """Delete and delete a feature."""
    feature_id = "FRA"

    # get one feature
    fra = api.get_space_feature(space_id=space_id, feature_id=feature_id)

    # delete feature
    api.delete_space_feature(space_id=space_id, feature_id=feature_id)

    # add back the previously deleted feature
    api.put_space_feature(space_id=space_id, feature_id=feature_id, data=fra)

    # patch the previously deleted feature
    api.patch_space_feature(
        space_id=space_id,
        feature_id=feature_id,
        data=fra,
        add_tags=["foo", "bar"],
    )

    api.patch_space_feature(
        space_id=space_id, feature_id=feature_id, data=fra, remove_tags=["bar"]
    )

    # get two features
    deu = api.get_space_feature(space_id=space_id, feature_id="DEU")
    ita = api.get_space_feature(space_id=space_id, feature_id="ITA")

    api.delete_space_features(space_id=space_id, id=["DEU", "ITA"])

    data = dict(type="FeatureCollection", features=[deu, ita])
    api.post_space_features(space_id=space_id, data=data)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_backoff():
    """Test backoff/retry an external (non XYZ-Hub) API call."""

    @backoff.on_exception(backoff.expo, TooManyRequestsException)
    def backoff_api_call():
        if random.random() > 0.7:
            resp = requests.get("http://httpstat.us/200")
        else:
            resp = requests.get("http://httpstat.us/429")
        if resp.status_code == 429:
            raise TooManyRequestsException(resp)
        else:
            return "success"

    assert backoff_api_call() == "success"
