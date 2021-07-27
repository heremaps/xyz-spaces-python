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

from xyzspaces.datasets import MICROSOFT_BUILDINGS_SPACE_ID
from xyzspaces.exceptions import ApiError
from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_spaces(api):
    """Get list of spaces."""
    spaces = api.get_spaces()
    assert "id" in spaces[0]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space(api, space_id):
    """Get single feature from space."""
    space = api.get_space(space_id=space_id, params={})
    assert "id" in space


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_features(api, space_id):
    """Get single feature from space."""
    feats = api.get_space_features(space_id=space_id, feature_ids=["GER", "BRA"])
    assert feats["type"] == "FeatureCollection"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_iterate(api, space_id):
    """Get all features from space by iterating over them."""
    stats = api.get_space_count(space_id=space_id)
    feature_gen = api.get_space_iterate(space_id=space_id, limit=100)
    assert len(list(feature_gen)) == stats["count"]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_delete_space_feature(api, space_id):
    """Get delete single feature from space."""
    id = "USA"
    feat = api.get_space_feature(space_id=space_id, feature_id=id)
    assert feat.get("id") == id
    api.delete_space_feature(space_id=space_id, feature_id=id)
    with pytest.raises(ApiError) as execinfo:
        resp = api.get_space_feature(space_id=space_id, feature_id=id)
    resp = execinfo.value.args[0]
    assert resp.status_code == 404
    assert resp.reason == "Not Found"
    assert resp.json()["errorMessage"] == "The requested resource does not exist."


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_delete_space_features(api, space_id):
    """Get delete features from space."""
    ids = ["ITA", "BRA"]
    for id in ids:
        feat = api.get_space_feature(space_id=space_id, feature_id=id)
        assert feat.get("id") == id
    api.delete_space_features(space_id=space_id, id=ids)
    for id in ids:
        with pytest.raises(ApiError) as execinfo:
            resp = api.get_space_feature(space_id=space_id, feature_id=id)
        resp = execinfo.value.args[0]
        assert resp.status_code == 404
        assert resp.reason == "Not Found"
        assert resp.json()["errorMessage"] == "The requested resource does not exist."


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_tile(api, space_id, point_space_id):
    """Get space tile."""
    tile = api.get_space_tile(
        space_id=space_id,
        tile_type="here",
        tile_id="12",
        params={"name!": "India"},
    )
    assert len(tile["features"]) == 97
    assert tile["type"] == "FeatureCollection"

    tile = api.get_space_tile(space_id=space_id, tile_type="here", tile_id="12", limit=10)
    assert len(tile["features"]) <= 10
    assert tile["type"] == "FeatureCollection"

    tile = api.get_space_tile(
        space_id=space_id,
        tile_type="here",
        tile_id="12",
        tags=["non-existing"],
    )
    assert len(tile["features"]) == 0
    assert tile["type"] == "FeatureCollection"

    tile = api.get_space_tile(
        space_id=space_id,
        tile_type="here",
        tile_id="12",
        selection=["p.color"],
    )
    assert tile["features"][0]["properties"] == {}

    tile1 = api.get_space_tile(
        space_id=point_space_id,
        tile_type="web",
        tile_id="8_65_95",
        clustering="hexbin",
        clusteringParams={"resolution": "0"},
    )
    assert tile1["features"][0]["geometry"]["type"] == "Polygon"
    assert tile1["features"][0]["properties"]["resolution"] == 0

    tile2 = api.get_space_tile(
        space_id=point_space_id,
        tile_type="web",
        tile_id="8_65_95",
        clustering="hexbin",
        clusteringParams={"resolution": "0"},
        margin=100,
    )
    # just checking that if margin param has any effect on response
    assert tile1 == tile2


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_tile_sampling(api):
    """Get space tile and compare all available sampling rates."""
    params = dict(
        space_id=MICROSOFT_BUILDINGS_SPACE_ID,
        tile_type="web",
        tile_id="11_585_783",
    )

    get_tile = api.get_space_tile
    tile_viz_off = get_tile(mode="viz", viz_sampling="off", **params)
    tile_viz_low = get_tile(mode="viz", viz_sampling="low", **params)
    tile_viz_med = get_tile(mode="viz", viz_sampling="med", **params)
    tile_viz_high = get_tile(mode="viz", viz_sampling="high", **params)

    len_viz_off = len(tile_viz_off["features"])
    len_viz_low = len(tile_viz_low["features"])
    len_viz_med = len(tile_viz_med["features"])
    len_viz_high = len(tile_viz_high["features"])
    assert len_viz_off >= len_viz_low > len_viz_med >= len_viz_high


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_bbox(api, space_id):
    """Get space bbox."""
    bb = [0, 0, 20, 20]  # [w, s, e, n]
    bbox = api.get_space_bbox(space_id=space_id, bbox=bb)
    assert len(bbox["features"]) == 15
    assert bbox["type"] == "FeatureCollection"

    bbox = api.get_space_bbox(space_id=space_id, bbox=bb, limit=10)
    assert len(bbox["features"]) <= 10
    assert bbox["type"] == "FeatureCollection"

    bbox = api.get_space_bbox(space_id=space_id, bbox=bb, tags="non-existing")
    assert len(bbox["features"]) == 0
    assert bbox["type"] == "FeatureCollection"

    resp = api.get_space_bbox(space_id=space_id, bbox=bb, params={"p.name": "Ghana"})
    assert len(resp["features"]) == 1
    assert resp["type"] == "FeatureCollection"

    bbox = api.get_space_bbox(space_id=space_id, bbox=bb, selection=["p.name"])
    assert bbox["features"][0]["properties"]["name"] == "Benin"

    bbox = api.get_space_bbox(space_id=space_id, bbox=bb, clustering="hexbin")
    assert bbox["features"][0]["properties"]["kind"] == "H3"

    bbox = api.get_space_bbox(
        space_id=space_id,
        bbox=bb,
        clustering="hexbin",
        clusteringParams={"resolution": "0"},
    )
    assert bbox["features"][0]["properties"]["resolution"] == 0


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_all(api, space_id):
    """Get all features in the space."""
    fc = api.get_space_all(space_id=space_id, limit=100)
    assert len(fc["features"]) == 180
    assert fc["type"] == "FeatureCollection"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_spatial(api, space_id, point_space_id):
    """Get all features in the space using spatial search by radius."""
    sp_resp1 = api.get_space_spatial(
        space_id=space_id,
        lat=37.377228699000057,
        lon=74.512691691000043,
        selection=["p.@ns:com:here:xyz"],
    )
    assert sp_resp1["type"] == "FeatureCollection"
    assert sp_resp1["features"][0]["id"] == "AFG"
    assert "name" not in sp_resp1["features"][0]["properties"]

    sp_resp2 = api.get_space_spatial(
        space_id=space_id,
        lat=37.377228699000057,
        lon=74.512691691000043,
        radius=100000,
    )
    assert sp_resp2["type"] == "FeatureCollection"
    assert sp_resp2["features"][0]["id"] == "AFG"
    assert sp_resp2["features"][1]["id"] == "CHN"
    assert sp_resp2["features"][2]["id"] == "PAK"
    assert sp_resp2["features"][3]["id"] == "TJK"

    sp_resp3 = api.get_space_spatial(
        space_id=point_space_id, ref_space_id=space_id, ref_feature_id="USA"
    )
    assert sp_resp3["type"] == "FeatureCollection"
    assert sp_resp3["features"][0]["properties"]["title"] == "Lincoln Park"

    sp_resp3 = api.get_space_spatial(
        space_id=point_space_id,
        ref_space_id=space_id,
        ref_feature_id="USA",
        limit=2,
    )
    assert sp_resp3["type"] == "FeatureCollection"
    assert len(sp_resp3["features"]) == 2

    sp_resp4 = api.get_space_spatial(
        space_id=space_id,
        lat=37.377228699000057,
        lon=74.512691691000043,
        tags=["non-existing"],
    )
    assert len(sp_resp4["features"]) == 0

    sp_resp5 = api.get_space_spatial(
        space_id=space_id,
        lat=37.377228699000057,
        lon=74.512691691000043,
        params={"p.name": "non-existing"},
    )
    assert len(sp_resp5["features"]) == 0

    with pytest.raises(ValueError):
        api.get_space_spatial(space_id=space_id, lat=37.377228699000057)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_post_spatial(api, space_id, point_space_id):
    """Get features which intersects the provided geometry."""
    data1 = {"type": "Point", "coordinates": [72.8557, 19.1526]}
    sp_resp1 = api.post_space_spatial(
        space_id=space_id, data=data1, selection=["p.@ns:com:here:xyz"]
    )
    assert sp_resp1["type"] == "FeatureCollection"
    assert sp_resp1["features"][0]["id"] == "IND"
    assert "name" not in sp_resp1["features"][0]["properties"]

    data2 = {
        "type": "Point",
        "coordinates": [74.512691691000043, 37.377228699000057],
    }

    sp_resp2 = api.post_space_spatial(space_id=space_id, data=data2, radius=100000)
    assert sp_resp2["type"] == "FeatureCollection"
    assert sp_resp2["features"][0]["id"] == "AFG"
    assert sp_resp2["features"][1]["id"] == "CHN"
    assert sp_resp2["features"][2]["id"] == "PAK"
    assert sp_resp2["features"][3]["id"] == "TJK"
    sp_resp3 = api.post_space_spatial(
        space_id=space_id, data=data2, radius=100000, limit=2
    )
    assert len(sp_resp3["features"]) == 2

    sp_resp4 = api.post_space_spatial(
        space_id=space_id, data=data1, tags=["non-existing"]
    )
    assert len(sp_resp4["features"]) == 0

    sp_resp5 = api.post_space_spatial(
        space_id=space_id, data=data1, params={"p.name": "non-existing"}
    )
    assert len(sp_resp5["features"]) == 0
