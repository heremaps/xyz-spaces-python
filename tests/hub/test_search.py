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
Module for testing various endpoints quickly to increase test code coverage.

These tests should be spread over other modules, soon...
"""

import pytest

from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_search(api, space_id):
    """Get all features from space by searching them."""
    feats = api.get_space_search(space_id=space_id)
    assert feats["type"] == "FeatureCollection"
    assert len(feats["features"]) > 0

    feats = api.get_space_search(space_id=space_id, limit=10)
    assert feats["type"] == "FeatureCollection"
    assert len(feats["features"]) <= 10

    feats = api.get_space_search(space_id=space_id, tags=["non-existing"])
    assert feats["type"] == "FeatureCollection"
    assert len(feats["features"]) == 0

    feats = api.get_space_search(space_id=space_id, params={"f.id=lte": "AGO"})
    assert len(feats["features"]) == 2

    feats = api.get_space_search(space_id=space_id, params={"f.id": "IND"})
    assert feats["features"][0]["id"] == "IND"

    feats = api.get_space_search(
        space_id=space_id, selection=["p.color"], params={"f.id": "IND"}
    )
    assert feats["features"][0]["properties"] == {}
