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
"""Tests for layer module."""
import geopandas
import pytest
from geojson import Feature, FeatureCollection, Point

from tests.iml.conftest import env_setup_done
from xyzspaces.iml.layer import HexbinClustering, InteractiveMapApiResponse

# Read operation on layer.


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_statistics(read_layer):
    """Test statistics of interactive map layer."""
    stats = read_layer.statistics
    assert stats["count"]["value"] == 179
    assert str(read_layer) == "layer_id: countries"


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_get_feature(read_layer):
    """Test get single feature from interactive map layer."""
    int_resp = read_layer.get_feature(feature_id="IND", selection=["name"])
    feature = int_resp.to_geojson()
    assert isinstance(feature, Feature)
    assert feature["id"] == "IND"
    with pytest.raises(NotImplementedError):
        int_resp.to_geopandas()


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_get_features(read_layer):
    """Test get multiple features from interactive map layer."""
    feature_ids = ["IND", "DEU", "USA"]
    int_resp = read_layer.get_features(
        feature_ids=feature_ids, selection=["name"], force_2d=True
    )
    fc = int_resp.to_geojson()
    assert isinstance(fc, FeatureCollection)
    for f in fc["features"]:
        assert f["id"] in feature_ids
    gdf = int_resp.to_geopandas()
    assert isinstance(gdf, geopandas.GeoDataFrame)
    with pytest.raises(ValueError):
        read_layer.get_features(feature_ids=[])


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_search_features(read_layer):
    """Test search features."""
    int_resp = read_layer.search_features(
        params={"p.name": "India"},
        selection=["name"],
    )
    fc = int_resp.to_geojson()
    assert isinstance(fc, FeatureCollection)
    assert fc["features"][0]["id"] == "IND"


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_iter_feature(read_layer):
    """Test iter features"""
    itr = read_layer.iter_features(selection=["name"])
    feature = next(itr)
    assert isinstance(feature, Feature)


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_get_features_in_bounding_box(read_layer):
    """Test features in bounding box."""
    clustering = HexbinClustering(absolute_resolution=1)
    int_resp = read_layer.get_features_in_bounding_box(
        bounds=(68.1766451354, 7.96553477623, 97.4025614766, 35.4940095078),
        clustering=clustering,
        selection=["name"],
    )
    fc = int_resp.to_geojson()
    assert isinstance(fc, FeatureCollection)


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_spatial_search(read_layer):
    """Test spatial search."""
    int_resp = read_layer.spatial_search(lng=73, lat=19, radius=1000, selection=["name"])
    fc = int_resp.to_geojson()
    assert fc["features"][0]["id"] == "IND"


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_spatial_search_geometry(read_layer):
    """Test spatial search using geometry."""
    pt = Point((73, 19))
    feature = Feature(geometry=pt)
    int_resp = read_layer.spatial_search_geometry(
        geometry=feature, radius=1000, selection=["name"]
    )
    fc = int_resp.to_geojson()
    assert fc["features"][0]["id"] == "IND"


def test_inavlid_response():
    """Test invalid response from interactive api."""
    resp = InteractiveMapApiResponse({"type": "dummy"})
    with pytest.raises(NotImplementedError):
        resp.to_geojson()
