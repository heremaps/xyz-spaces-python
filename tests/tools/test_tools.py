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
Module for testing xyzspaces.tools.

Here we don't generate any temporary spaces.
"""

import pytest

from xyzspaces.config.default import XYZConfig
from xyzspaces.datasets import get_countries_data
from xyzspaces.tools import subset_geojson
from xyzspaces.utils import feature_to_bbox, get_xyz_token

XYZ_TOKEN = get_xyz_token()
gj_countries = get_countries_data()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_is_empty():
    """Test subset GeoJSON by tile returns empty list of features."""
    subset = subset_geojson(
        config=XYZConfig.from_default(),
        gj=gj_countries,
        bbox=[0, 0, 0, 0],
        clip=False,
    )
    assert subset["features"] == []


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_is_empty_2():
    """Test subset GeoJSON by tile returns only one feature for Germany."""
    subset = subset_geojson(
        config=XYZConfig.from_default(),
        gj=gj_countries,
        bbox=[13, 51, 14, 52],  # w, s, e, n
        clip=False,
    )
    assert len(subset["features"]) == 1
    assert subset["features"][0]["properties"]["name"] == "Germany"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_is_empty_3():
    """Test subset GeoJSON by tile returns only one feature for Germany."""
    subset = subset_geojson(
        config=XYZConfig.from_default(),
        gj=gj_countries,
        bbox=[13, 51, 14, 52],
        clip=True,  # w, s, e, n
    )
    assert len(subset["features"]) == 1
    assert subset["features"][0]["geometry"]["coordinates"] == [
        [[13, 51, 0], [13, 52, 0], [14, 52, 0], [14, 51, 0], [13, 51, 0]]
    ]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_bbox_feature():
    """Test subset GeoJSON by tile."""
    subset = subset_geojson(
        config=XYZConfig.from_default(), gj=gj_countries, bbox=[13, 51, 14, 52]
    )
    assert feature_to_bbox(subset["features"][0]) == [
        5.988658,
        47.302488,
        15.016996,
        54.983104,
    ]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_raises1():
    """Test subset GeoJSON raises ValueError for bbox and tile_type."""
    with pytest.raises(ValueError):
        subset_geojson(
            config=XYZConfig.from_default(),
            gj=gj_countries,
            bbox=[13, 51, 14, 52],  # w, s, e, n
            tile_type="dummy",
            tile_id="1234",
            clip=False,
        )


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_raises2():
    """Test subset GeoJSON raises AssertionError w/o bbox and only tile_type."""
    with pytest.raises(AssertionError):
        subset_geojson(
            config=XYZConfig.from_default(),
            gj=gj_countries,
            tile_type="dummy",
            clip=False,
        )


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_bbox_raises3():
    """Test subset GeoJSON with tile type and ID returns a FeatureCollection."""
    subset = subset_geojson(
        config=XYZConfig.from_default(),
        gj=gj_countries,
        tile_type="here",
        tile_id="123",
        clip=False,
    )
    assert "type" in subset.keys()


@pytest.mark.skipif(True, reason="Not implemented yet.")
def test_superset_bbox():
    """Test superset GeoJSON to bbox."""
    pass


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_spatial_search():
    """Test subset GeoJSON with lat/lon/radius returns a FeatureCollection."""
    subset = subset_geojson(
        config=XYZConfig.from_default(),
        gj=gj_countries,
        lat=37.377228699000057,
        lon=74.512691691000043,
        radius=100000,
    )
    assert subset["type"] == "FeatureCollection"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_spatial_raises():
    """Test subset GeoJSON raises ``ValueError`` with lat, lon and bbox."""
    with pytest.raises(ValueError):
        subset_geojson(
            config=XYZConfig.from_default(),
            gj=gj_countries,
            bbox=[13, 51, 14, 52],  # w, s, e, n
            lat=37.377228699000057,
            lon=74.512691691000043,
        )


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_subset_spatial_raises2():
    """Test subset GeoJSON raises ``ValueError`` with lat, lon and tile_id, tile_type."""
    with pytest.raises(ValueError):
        subset_geojson(
            config=XYZConfig.from_default(),
            gj=gj_countries,
            tile_type="here",
            tile_id="123",
            lat=37.377228699000057,
            lon=74.512691691000043,
        )

    with pytest.raises(ValueError):
        subset_geojson(
            config=XYZConfig.from_default(),
            gj=gj_countries,
            tile_id="123",
            lat=37.377228699000057,
            lon=74.512691691000043,
        )
