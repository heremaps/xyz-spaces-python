# Copyright (C) 2019-2020 HERE Europe B.V.
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

"""Module for testing xyzspaces.spaces."""

import json
from pathlib import Path

import pytest
from geojson import GeoJSON

from xyzspaces import XYZ
from xyzspaces.datasets import get_chicago_parks_data, get_countries_data
from xyzspaces.exceptions import ApiError
from xyzspaces.spaces import Space
from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()
gj_countries = get_countries_data()
gj_chicago_parks = get_chicago_parks_data()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_create_from_id(api, space_id):
    """Test create from an existing space ID."""
    space = Space.from_id(space_id)
    assert space.info == api.get_space(space_id=space_id)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_new_space():
    """Test create and delete a new space."""
    # create space
    space = Space.new(title="Foo", description="Bar")
    assert space.info["title"] == "Foo"
    space_id = space.info["id"]
    # delete space
    space.delete()
    assert space.info == {}
    with pytest.raises(ApiError):
        space.read(id=space_id)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_create_delete_1(api):
    """Test create and delete a new space."""
    # create space
    space = Space.new(title="Foo", description="Bar")
    assert space.info["title"] == "Foo"
    print("created", space.info)
    id = space.info["id"]
    assert "id" in space.info

    # add features
    res = space.add_features(features=gj_countries)
    # get feature
    res = space.get_feature(feature_id="FRA")
    print(res)

    # delete space
    space.delete()
    print("deleted", id)
    assert space.info == {}
    # TODO: assert that accessing the deleted space causes an error...


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_feature(empty_space):
    """Test add feature to space."""
    space = empty_space

    # add features
    space.add_features(features=gj_countries)
    feature = space.get_feature(feature_id="FRA")
    assert type(feature) == GeoJSON
    assert feature["id"] == "FRA"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_search(space_object):
    """Test space search function for the space object."""
    feats = list(space_object.search())
    assert feats[0]["type"] == "Feature"
    assert len(feats) > 0

    feats = list(space_object.search(limit=10))
    assert feats[0]["type"] == "Feature"
    assert len(feats) <= 10

    feats = list(space_object.search(tags=["non-existing"]))
    assert len(feats) == 0

    feats = list(space_object.search(params={"p.name": "India"}))
    assert feats[0]["id"] == "IND"

    feats = list(space_object.search(params={"f.id": "IND"}))
    assert feats[0]["id"] == "IND"

    feats = list(
        space_object.search(selection=["p.color"], params={"f.id": "IND"})
    )
    assert "properties" not in feats[0].keys()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_iterator(space_object):
    """Get all features from space by iterating over them."""
    stats = space_object.get_statistics()
    feature_gen = space_object.iter_feature()
    assert len(list(feature_gen)) == stats["count"]["value"]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_feature_operations(space_object):
    """Test for get, add, update and delete feature operations."""
    feature_id = "FRA"

    # get one feature
    fra = space_object.get_feature(feature_id)
    assert isinstance(fra, GeoJSON)

    # delete feature
    space_object.delete_feature(feature_id=feature_id)

    # add back the previously deleted feature
    res = space_object.add_feature(feature_id=feature_id, data=fra)
    assert isinstance(res, GeoJSON)

    res = space_object.update_feature(
        feature_id=feature_id, data=fra, add_tags=["foo", "bar"],
    )
    assert isinstance(res, GeoJSON)

    res = space_object.update_feature(
        feature_id=feature_id, data=fra, remove_tags=["bar"]
    )

    assert isinstance(res, GeoJSON)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_features_operations(space_object):
    """Test for get, add, update and delete features operations."""
    # get two features
    data = space_object.get_features(feature_ids=["DEU", "ITA"])
    assert isinstance(data, GeoJSON)

    space_object.delete_features(feature_ids=["DEU", "ITA"])

    res = space_object.add_features(features=data)
    assert isinstance(res, GeoJSON)

    data["features"][0]["id"] = "test1"
    data["features"][1]["id"] = "test2"

    res = space_object.update_features(features=data, add_tags=["foo", "bar"])
    assert isinstance(res, GeoJSON)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_features_search_operations(space_object):
    """Test for bbox, tile and spatial search  operations."""
    bbox = list(space_object.features_in_bbox(bbox=[0, 0, 20, 20]))
    assert len(bbox) == 15
    assert bbox[0]["type"] == "Feature"

    tile = list(space_object.features_in_tile(tile_type="here", tile_id="12"))
    assert len(tile) == 97
    assert tile[0]["type"] == "Feature"

    spatial_search = list(
        space_object.spatial_search(
            lat=37.377228699000057, lon=74.512691691000043
        )
    )
    assert spatial_search[0]["type"] == "Feature"
    assert spatial_search[0]["id"] == "AFG"

    data1 = {"type": "Point", "coordinates": [72.8557, 19.1526]}
    spatial_search_geom = list(
        space_object.spatial_search_geometry(data=data1)
    )
    assert spatial_search_geom[0]["type"] == "Feature"
    assert spatial_search_geom[0]["id"] == "IND"
    with pytest.raises(ValueError):
        list(space_object.features_in_tile(tile_type="dummy", tile_id="12"))


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_add_features_from_files_without_altitude(
    space_object, tmp_path
):
    """Test for adding features using csv and geojson."""
    fp_csv = Path(__file__).parents[1] / "data" / "test.csv"
    space_object.add_features_csv(
        fp_csv, lat_col="latitude", lon_col="longitude", id_col="policyID"
    )
    feature = space_object.get_feature(feature_id="333743")
    assert feature["type"] == "Feature"

    fp_geojson = Path(__file__).parents[1] / "data" / "test.geojson"
    space_object.add_features_geojson(fp_geojson)

    feature = space_object.get_feature(feature_id="test_geojson_1")
    assert feature["type"] == "Feature"
    geo_data_dict = {
        "type": "Feature",
        "id": "test_id",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "properties": {"name": "Dinagat Islands"},
    }
    geo_data = json.dumps(geo_data_dict)
    temp_file = Path(tmp_path) / "temp.geojson"
    with open(temp_file, "w") as f:
        f.write(geo_data)
    space_object.add_features_geojson(temp_file)
    feature = space_object.get_feature(feature_id="test_id")
    assert feature["type"] == "Feature"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_add_features_from_files_with_altitude(space_object):
    """Test for adding features using csv and geojson."""
    fp_csv = Path(__file__).parents[1] / "data" / "test_altitude.csv"
    space_object.add_features_csv(
        fp_csv,
        lat_col="latitude",
        lon_col="longitude",
        id_col="policyID",
        alt_col="altitude",
    )
    feature = space_object.get_feature(feature_id="333743")
    assert feature["type"] == "Feature"

    fp_geojson = Path(__file__).parents[1] / "data" / "test_altitude.geojson"
    space_object.add_features_geojson(fp_geojson)
    feature = space_object.get_feature(feature_id="test_geojson_1")
    assert feature["type"] == "Feature"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_virtual_space_group(upstream_spaces):
    """Test virtual-space with group operation."""
    # Test group operation on upstream spaces.
    title = "Virtual Space for coutries and chicago parks data"
    description = "Test group functionality of virtual space"
    kwargs = {"virtualspace": dict(group=upstream_spaces)}
    vspace = Space.virtual(title=title, description=description, **kwargs)
    vpace_stats = vspace.get_statistics()
    assert set(vpace_stats["geometryTypes"]["value"]) == {
        "MultiPolygon",
        "Polygon",
        "Point",
    }
    assert vpace_stats["count"]["value"] == 189
    feature1 = vspace.get_feature(feature_id="FRA")
    assert (
        feature1["properties"]["@ns:com:here:xyz"]["space"]
        == upstream_spaces[0]
    )
    feature2 = vspace.get_feature(feature_id="LP")
    assert (
        feature2["properties"]["@ns:com:here:xyz"]["space"]
        == upstream_spaces[1]
    )
    vspace.delete_feature(feature_id="FRA")
    with pytest.raises(ApiError):
        vspace.get_feature("FRA")
    sp1 = Space.from_id(space_id=upstream_spaces[0])
    with pytest.raises(ApiError):
        sp1.get_feature("FRA")
    vspace.delete()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_virtual_space_merge(space_id, empty_space):
    """Test virtual-space with a merge operation."""
    # Creating duplicate space_id and checking post merge there are no duplicate features.
    empty_space.add_features(features=gj_countries)
    title = "Virtual Space to check merge operation"
    description = "Test merge functionality of virtual space"
    kwargs = {"virtualspace": {"merge": [space_id, empty_space.info["id"]]}}
    vspace = Space.virtual(title=title, description=description, **kwargs)
    feature = vspace.get_feature(feature_id="FRA")
    assert feature["properties"]["@ns:com:here:xyz"]["space"] is None
    vspace.delete()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_virtual_space_override(space_id, empty_space):
    """Test virtual-space with override operation."""
    # Creating duplicate space_id and checking post override operation on virtual-space
    # duplicate features from 2nd space in list of upstream spaces get overridden.
    empty_space.add_features(features=gj_countries)
    title = "Virtual Space to check merge operation"
    description = "Test merge functionality of virtual space"
    kwargs = {"virtualspace": {"override": [space_id, empty_space.info["id"]]}}
    vspace = Space.virtual(title=title, description=description, **kwargs)
    feature = vspace.get_feature(feature_id="FRA")
    assert (
        feature["properties"]["@ns:com:here:xyz"]["space"]
        == empty_space.info["id"]
    )
    vspace.delete()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_virtual_space_custom(space_id, empty_space):
    """Test virtual-space with custom operation."""
    empty_space.add_features(features=gj_countries)
    title = "Virtual Space to check merge operation"
    description = "Test merge functionality of virtual space"
    kwargs = {"virtualspace": {"custom": [space_id, empty_space.info["id"]]}}
    vspace = Space.virtual(title=title, description=description, **kwargs)
    # TODO: Add assertions once custom connector is enabled for token.
    vspace.delete()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_spaces_list(space_id):
    """Test get list of spaces."""
    obj = XYZ()
    spaces_list = obj.spaces.list()
    assert len(spaces_list) > 0


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_update_space(space_id, empty_space):
    """Test update space title and description."""
    obj = XYZ(credentials=XYZ_TOKEN)
    space = obj.spaces.from_id(space_id=space_id)
    with pytest.raises(ValueError):
        space.update(title="", description="")
    title = "New Title"
    res1 = space.update(title=title)
    assert res1["title"] == title
    description = "New Description"
    res2 = space.update(description=description)
    assert res2["description"] == description
    # test tagging rules
    tagging_rules = {
        "large": "$.features[?(@.properties.area>=500)]",
        "small": "$.features[?(@.properties.area<500)]",
    }
    title = "New tagging Title"
    description = "New tagging Description"
    res = empty_space.update(
        title=title, description=description, tagging_rules=tagging_rules
    )
    assert res["title"] == title
    assert res["description"] == description
    empty_space.add_features(features=gj_chicago_parks)
    large_parks = empty_space.search(tags=["large"])
    for park in large_parks:
        assert park["id"] in ["LP", "BP", "JP"]
    small_parks = empty_space.search(tags=["small"])
    for park in small_parks:
        assert park["id"] in ["MP", "GP", "HP", "DP", "CP", "COP"]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_clustering(space_object, empty_space):
    """Test clustering."""
    res = space_object.cluster(clustering="hexbin")
    assert res["type"] == "FeatureCollection"
    with pytest.raises(Exception):
        empty_space.cluster(clustering="hexbin")


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_coordinates_with_altitude(empty_space):
    """Test geojson data having altitude information."""
    fp_geojson = (
        Path(__file__).parents[2]
        / "xyzspaces"
        / "datasets"
        / "chicago_parks.geo.json"
    )
    space = empty_space
    space.add_features_geojson(fp_geojson, encoding="utf-8-sig")
    stats = space.get_statistics()
    assert stats["count"]["value"] == 9
    assert stats["geometryTypes"]["value"] == ["Point"]
    feature = space.get_feature(feature_id="LP")
    assert feature.id == "LP"
    assert feature.geometry["coordinates"] == [-87.637596, 41.940403, 4.0]
    tagging_rules = {"large": "$.features[?(@.properties.area>=500)]"}
    _ = space.update(tagging_rules=tagging_rules)
    large_parks = empty_space.search(tags=["large"])
    for park in large_parks:
        assert park["id"] in ["LP", "BP", "JP"]
    feature_iter = space.iter_feature()
    feature = next(feature_iter)
    assert feature["geometry"]["coordinates"] == [-87.637596, 41.940403, 4]
    res = space.cluster(clustering="hexbin")
    assert res["type"] == "FeatureCollection"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_read(space_object, space_id):
    """Test read space."""
    space = space_object.read(id=space_id)
    assert space.info["title"] == "Testing xyzspaces"
    assert (
        space.info["description"]
        == "Temporary space containing countries data."
    )


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_geojson_exception(space_object, tmp_path):
    """Test exception cases for add features using geojson."""
    temp_file = Path(tmp_path) / "temp.geojson"
    geo_data_dict = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [125.6, 10.1]},
        "properties": {"name": "Dinagat Islands"},
    }
    geo_data = json.dumps(geo_data_dict)
    with open(temp_file, "w") as f:
        f.write(geo_data)
    with pytest.raises(Exception):
        space_object.add_features_geojson(temp_file)

    geo_data = geo_data.replace("Feature", "dummy")
    with open(temp_file, "w") as f:
        f.write(geo_data)
    with pytest.raises(Exception):
        space_object.add_features_geojson(temp_file)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_csv_exception(space_object, tmp_path):
    """Test exception cases for add features using csv."""
    assert repr(space_object) == f"space_id: {space_object.info['id']}"
    temp_file = Path(tmp_path) / "temp.csv"
    csv_data = """dummy_a,dummy_b,dummy_c
                  1,2,3"""
    with open(temp_file, "w") as f:
        f.write(csv_data)
    with pytest.raises(Exception):
        space_object.add_features_csv(
            temp_file, lon_col="", lat_col="", id_col=""
        )


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_bulk_upload(space_object):
    geo_file = Path(__file__).parents[1] / "data" / "road_traffic.geo.json"

    with open(geo_file) as fh:
        data = json.load(fh)

    space_object.add_features(data, features_size=5000, chunk_size=2)
    ft = space_object.get_feature("1158230457T")
    assert ft["type"] == "Feature"
    assert ft["properties"]["segment"] == "1158230457T"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_file_bulk_upload(space_object):
    geo_file = Path(__file__).parents[1] / "data" / "road_traffic.geo.json"
    space_object.add_features_geojson(geo_file, features_size=5000)
    ft = space_object.get_feature("1158230457T")
    assert ft["type"] == "Feature"
    assert ft["properties"]["segment"] == "1158230457T"
