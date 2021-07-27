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

"""Module for testing xyzspaces.spaces."""

import json
from pathlib import Path
from time import sleep

import geopandas as gpd
import pytest
from geojson import GeoJSON

from xyzspaces import XYZ
from xyzspaces.datasets import (
    MICROSOFT_BUILDINGS_SPACE_ID,
    get_chicago_parks_data,
    get_countries_data,
    get_microsoft_buildings_space,
)
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


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_new_space():
    """Test create and delete a new space."""
    # create space
    space = Space.new(title="Foo", description="Bar")
    sleep(0.5)
    space_info = space.info
    assert space_info["title"] == "Foo"
    assert "shared" not in space_info
    assert not space.isshared()
    space_id = space.info["id"]
    # delete space
    space.delete()
    sleep(1)
    assert space.info == {}
    with pytest.raises(ApiError):
        space.read(id=space_id)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_create_delete_1(api):
    """Test create and delete a new space."""
    # create space
    space = Space.new(title="Foo", description="Bar")
    sleep(0.5)
    assert space.info["title"] == "Foo"
    assert "id" in space.info

    # add features
    _ = space.add_features(features=gj_countries)
    # get feature
    _ = space.get_feature(feature_id="FRA")

    # delete space
    space.delete()
    assert space.info == {}
    # TODO: assert that accessing the deleted space causes an error...


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_feature(empty_space):
    """Test add feature to space."""
    space = empty_space

    # add features
    space.add_features(features=gj_countries)
    feature = space.get_feature(feature_id="FRA")
    space.add_features(features=feature)
    assert type(feature) == GeoJSON
    assert feature["id"] == "FRA"
    del feature["id"]
    resp = space.add_feature(data=feature)
    assert type(resp["features"][0]["id"]) == str
    with pytest.raises(Exception):
        space.add_features(data={"features": [], "type": "FeatureCollection"})


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_search(space_object):
    """Test space search function for the space object."""
    feats = list(space_object.search())
    assert feats[0]["type"] == "Feature"
    assert len(feats) > 0

    feats = space_object.search(limit=10, geo_dataframe=True)
    gdf = next(feats)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf["name"][0] == "Afghanistan"

    feats = list(space_object.search(tags=["non-existing"]))
    assert len(feats) == 0

    feats = list(space_object.search(params={"p.name": "India"}))
    assert feats[0]["id"] == "IND"

    feats = list(space_object.search(params={"f.id": "IND"}))
    assert feats[0]["id"] == "IND"

    feats = list(space_object.search(selection=["p.color"], params={"f.id": "IND"}))
    assert feats[0]["properties"] == {}


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
        feature_id=feature_id,
        data=fra,
        add_tags=["foo", "bar"],
    )
    assert isinstance(res, GeoJSON)

    res = space_object.update_feature(
        feature_id=feature_id, data=fra, remove_tags=["bar"]
    )

    assert isinstance(res, GeoJSON)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_features_operations(space_object):
    """Test for get, add, update and delete features operations."""
    gdf = space_object.get_features(feature_ids=["DEU", "ITA"], geo_dataframe=True)
    assert isinstance(gdf, gpd.GeoDataFrame)
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

    gdf = next(space_object.features_in_bbox(bbox=[0, 0, 20, 20], geo_dataframe=True))
    assert gdf.shape == (15, 4)

    spatial_search = list(
        space_object.spatial_search(lat=37.377228699000057, lon=74.512691691000043)
    )
    assert spatial_search[0]["type"] == "Feature"
    assert spatial_search[0]["id"] == "AFG"

    ss_gdf = next(
        space_object.spatial_search(
            lat=37.377228699000057, lon=74.512691691000043, geo_dataframe=True
        )
    )
    assert ss_gdf.shape == (1, 4)

    data1 = {"type": "Point", "coordinates": [72.8557, 19.1526]}
    spatial_search_geom = list(space_object.spatial_search_geometry(data=data1))
    assert spatial_search_geom[0]["type"] == "Feature"
    assert spatial_search_geom[0]["id"] == "IND"
    ss_gdf = next(space_object.spatial_search_geometry(data=data1, geo_dataframe=True))
    assert ss_gdf.shape == (1, 4)
    with pytest.raises(ValueError):
        list(space_object.features_in_tile(tile_type="dummy", tile_id="12"))
    res = space_object.features_in_tile(
        tile_type="here", tile_id="12", limit=10, geo_dataframe=True
    )
    gdf = next(res)
    assert gdf.shape == (10, 4)
    res = space_object.features_in_tile(tile_type="here", tile_id="12", limit=10)
    features = list(res)
    assert features[0]["id"] == "AFG"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_add_features_from_files_without_altitude(empty_space, tmp_path):
    """Test for adding features using csv and geojson."""
    fp_csv = Path(__file__).parents[1] / "data" / "test.csv"
    space = empty_space
    space.add_features_csv(
        fp_csv, lon_col="longitude", lat_col="latitude", id_col="policyID"
    )
    feature = space.get_feature(feature_id="333743")
    assert feature["type"] == "Feature"

    fp_geojson = Path(__file__).parents[1] / "data" / "test.geojson"
    space.add_features_geojson(fp_geojson)

    feature = space.get_feature(feature_id="test_geojson_1")
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
    space.add_features_geojson(temp_file)
    feature = space.get_feature(feature_id="test_id")
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
    assert feature1["properties"]["@ns:com:here:xyz"]["space"] == upstream_spaces[0]
    feature2 = vspace.get_feature(feature_id="LP")
    assert feature2["properties"]["@ns:com:here:xyz"]["space"] == upstream_spaces[1]
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
    kwargs = {"virtualspace": {"merge": [space_id, empty_space.info["id"]]}}
    vspace = Space.virtual(title=title, **kwargs)
    feature = vspace.get_feature(feature_id="FRA")
    assert feature["properties"]["@ns:com:here:xyz"].get("space") is None
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
    assert feature["properties"]["@ns:com:here:xyz"]["space"] == empty_space.info["id"]
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


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_update_space(space_id, empty_space):
    """Test update space title and description."""
    obj = XYZ()
    space = obj.spaces.from_id(space_id=space_id)
    title = "New Title"
    res1 = space.update(title=title)
    assert res1["title"] == title
    description = "New Description"
    res2 = space.update(description=description)
    assert res2["description"] == description

    res3 = space.update(shared=True)
    assert res3["shared"]
    assert space.isshared()
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


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_coordinates_with_altitude(empty_space):
    """Test geojson data having altitude information."""
    fp_geojson = (
        Path(__file__).parents[2] / "xyzspaces" / "datasets" / "chicago_parks.geo.json"
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
    assert space.info["description"] == "Temporary space containing countries data."


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
            temp_file, lon_col="dummy_a", lat_col="dummy", id_col=""
        )


@pytest.mark.skipif(True, reason="Already getting covered in test_file_bulk_upload.")
def test_bulk_upload(space_object):
    geo_file = Path(__file__).parents[1] / "data" / "road_traffic.geo.json"

    with open(geo_file) as fh:
        data = json.load(fh)

    space_object.add_features(data, features_size=5000, chunk_size=2)
    ft = space_object.get_feature("1158230457T")
    assert ft["type"] == "Feature"
    assert ft["properties"]["segment"] == "1158230457T"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_file_bulk_upload(space_object):
    geo_file = Path(__file__).parents[2] / "xyzspaces" / "datasets" / "countries.geo.json"
    space_object.add_features_geojson(geo_file, features_size=50)
    ft = space_object.get_feature("IND")
    assert ft["type"] == "Feature"
    assert ft["properties"]["name"] == "India"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_schema_validation(space_object):
    schema = (
        '{"definitions":{},"$schema":"http://json-schema.org/draft-07/schema#",'
        '"$id":"http://example.com/root.json","type":"object",'
        '"title":"TheRootSchema","required":["geometry","type","properties"]}'
    )
    space_object.update(schema=schema)

    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {
                    "type": "Point",
                    "coordinates": [15.8319, -2.5913],
                },
                "type": "Feature",
                "properties": {"name": "Audi"},
            },
            {"type": "Feature", "properties": {"name": "Tesla"}},
        ],
    }

    try:
        space_object.add_features(features=feature_collection)
    except Exception as e:
        resp = e.args[0].json()
        assert resp["type"] == "ErrorResponse"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_schema_validation_new_space(schema_validation_space):
    """Test schema validation when creating a new space."""
    space = schema_validation_space
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {
                    "type": "Point",
                    "coordinates": [15.8319, -2.5913],
                },
                "type": "Feature",
                "properties": {"name": "Audi"},
            },
            {"type": "Feature", "properties": {"name": "Tesla"}},
        ],
    }

    try:
        space.add_features(features=feature_collection)
    except Exception as e:
        resp = e.args[0].json()
        assert resp["type"] == "ErrorResponse"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_activity_log(activity_log_space):
    """Test activity log."""

    space = activity_log_space
    # Adding some sleep as activity log is async activity
    sleep(5)
    space_info = space.info
    params = space_info["listeners"]["activity-log-writer"][0]
    assert type(params["params"]["spaceId"]) == str
    assert params["params"]["storageMode"] == "DIFF_ONLY"
    assert params["params"]["writeInvalidatedAt"] is True


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_new_shared_space(shared_space):
    """Test create and delete a new space."""
    assert shared_space.isshared()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_unshare_space(shared_space):
    """Test update space to unshare it."""
    shared_space.update(shared=False)
    space_info = shared_space.info
    assert not shared_space.isshared()
    # checking that there is no impact if we do not pass anything to update method.
    shared_space.update()
    space_info2 = shared_space.info
    del space_info["updatedAt"]
    del space_info2["updatedAt"]
    assert space_info == space_info2


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_microsoft_public_space():
    """Test to check microsoft buildings dataset space"""
    microsoft_space = get_microsoft_buildings_space()
    feature = microsoft_space.get_feature("4d34cdd884079966adc6e5a2228b10c5")
    assert feature["type"] == "Feature"
    assert feature["properties"]["city"] == "Slocomb"
    assert feature["properties"]["country"] == "USA"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_shapefile(empty_space):
    """Test uploading shapefile to the space."""
    space = empty_space
    shapefile = Path(__file__).parents[1] / "data" / "stations.zip"
    space.add_features_shapefile(f"zip://{shapefile}")
    resp = space.search(params={"p.name": "Van Dorn Street"})
    flist = list(resp)
    assert flist[0]["geometry"]["coordinates"] == [
        -77.12911152,
        38.79930767,
        0,
    ]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_wktfile(empty_space):
    """Test uploading wkt data"""
    space = empty_space
    wkt_file = Path(__file__).parents[1] / "data" / "test.wkt"
    space.add_features_wkt(path=wkt_file)
    features = []
    for f in space.iter_feature():
        features.append(f)
    assert len(features) == 6


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_wktfile_single_feature(empty_space, tmp_path):
    """Test uploading single feature in WKT file."""
    space = empty_space
    temp_file = Path(tmp_path) / "temp.wkt"
    with open(temp_file, "w") as f:
        f.write("POLYGON ((-80 25, -65 18, -64 32, -80 25))")
    space.add_features_wkt(path=temp_file)
    features = []
    for f in space.iter_feature():
        features.append(f)
    assert len(features) == 1


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_gpx(empty_space):
    """Test uploading gpx file to the space."""
    space = empty_space
    gpx_file = Path(__file__).parents[1] / "data" / "example.gpx"
    space.add_features_gpx(gpx_file, features_size=500)
    resp = space.search(params={"p.ele": "2376"})
    flist = list(resp)
    assert flist[0]["geometry"]["coordinates"] == [8.89241667, 46.57608333, 0]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_spatial_search_geometry_divided(large_data_space):
    """Test spatial search with divide functionality"""
    feature = dict(
        type="Feature",
        properties={},
        geometry={
            "type": "Polygon",
            "coordinates": [
                [[-120, 60], [120, 60], [120, -60], [-120, -60], [-120, 60]],
                [[-60, 30], [60, 30], [60, -30], [-60, -30], [-60, 30]],
            ],
        },
    )

    feature_read = list(
        large_data_space.spatial_search_geometry(
            data=feature["geometry"], divide=True, cell_width=1000000
        )
    )

    assert len(feature_read) == 7459
    assert feature_read[0]["type"] == "Feature"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_kml(empty_space):
    """Test uploading kml file to the space."""
    space = empty_space
    kml_file = Path(__file__).parents[1] / "data" / "test.kml"
    space.add_features_kml(kml_file, features_size=500)
    stats = space.get_statistics()
    assert stats["count"]["value"] == 243


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_geobuff(empty_space):
    """Test uploading geobuff file to the space."""
    space = empty_space
    geobuff_file = Path(__file__).parents[1] / "data" / "test.pbf"
    space.add_features_geobuf(geobuff_file, features_size=500)
    stats = space.get_statistics()
    assert stats["count"]["value"] == 180


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_duplicate_properties(empty_space):
    geojson_file = Path(__file__).parents[1] / "data" / "countries.geo.json"
    with open(geojson_file) as f:
        geojson = json.loads(f.read())
    for f in geojson["features"]:
        f.pop("id", None)
        f["properties"]["test"] = "test"
    empty_space.add_features(geojson, features_size=100, id_properties=["name", "test"])
    stats = empty_space.get_statistics()
    assert stats["count"]["value"] == 180
    assert empty_space.get_feature(feature_id="India-test")["type"] == "Feature"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_duplicate(empty_space):
    geojson_file = Path(__file__).parents[1] / "data" / "countries.geo.json"
    with open(geojson_file) as f:
        geojson = json.loads(f.read())
    for f in geojson["features"]:
        f.pop("id", None)
    empty_space.add_features(geojson, features_size=100)
    stats = empty_space.get_statistics()
    assert stats["count"]["value"] == 180


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_geopandas(empty_space):
    geojson_file = Path(__file__).parents[1] / "data" / "countries.geo.json"
    df = gpd.read_file(geojson_file)
    empty_space.add_features_geopandas(data=df)
    stats = empty_space.get_statistics()
    assert stats["count"]["value"] == 292


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test__gen_id_from_properties_exception():
    """Test exception is raised when feature has no properties."""
    space = Space()
    with pytest.raises(Exception):
        space._gen_id_from_properties(feature={}, id_properties=[])


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_add_features_shapefile_diff_projection(empty_space):
    """Test uploading shapefile to the space with different projection."""
    space = empty_space
    shapefile = Path(__file__).parents[1] / "data" / "stations-32633.zip"
    space.add_features_shapefile(f"zip://{shapefile}")
    resp = space.search(params={"p.name": "Van Dorn Street"})
    flist = list(resp)
    assert flist[0]["geometry"]["coordinates"] == [
        -77.12911152,
        38.79930767,
        0,
    ]


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_space_clone(space_object, space_id, empty_space):
    """Test space cloning functionality."""
    space = space_object.read(id=space_id)
    cloned_space = space.clone()
    cloned_specific_space = space.clone(space_id=empty_space.info["id"])
    assert cloned_space.get_statistics()["count"]["value"] == 180
    assert cloned_specific_space.get_statistics()["count"]["value"] == 180
    assert cloned_space.get_feature("IND")["properties"]["name"] == "India"
    assert cloned_specific_space.get_feature("IND")["properties"]["name"] == "India"


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_force_2d(space_object):
    """Test force2D parameter for all API's used to read feature"""
    feature = list(space_object.search(params={"p.name": "India"}, force_2d=True))
    assert len(feature[0]["geometry"]["coordinates"][0][0]) == 2

    feature = next(space_object.iter_feature(force_2d=True))
    assert len(feature["geometry"]["coordinates"][0][0]) == 2

    feature = space_object.get_feature(feature_id="FRA", force_2d=True)
    assert len(feature["geometry"]["coordinates"][0][0][0]) == 2

    data = space_object.get_features(feature_ids=["DEU", "ITA"], force_2d=True)
    assert len(data["features"][0]["geometry"]["coordinates"][0][0]) == 2

    bbox = list(space_object.features_in_bbox(bbox=[0, 0, 20, 20], force_2d=True))
    assert len(bbox[0]["geometry"]["coordinates"][0][0]) == 2

    spatial_search = list(
        space_object.spatial_search(
            lat=37.377228699000057, lon=74.512691691000043, force_2d=True
        )
    )
    assert len(spatial_search[0]["geometry"]["coordinates"][0][0]) == 2

    data1 = {"type": "Point", "coordinates": [72.8557, 19.1526]}
    spatial_search_geom = list(
        space_object.spatial_search_geometry(data=data1, force_2d=True)
    )
    assert len(spatial_search_geom[0]["geometry"]["coordinates"][0][0]) == 2

    res = space_object.features_in_tile(
        tile_type="here", tile_id="12", limit=10, force_2d=True
    )
    features = list(res)
    assert len(features[0]["geometry"]["coordinates"][0][0]) == 2


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_space_tile_sampling(api):
    """Get space tile and compare all available sampling rates."""
    space = Space.from_id(MICROSOFT_BUILDINGS_SPACE_ID)
    params = dict(
        tile_type="web",
        tile_id="11_585_783",
    )
    tile_viz_off = list(space.features_in_tile(mode="viz", viz_sampling="off", **params))
    tile_viz_low = list(space.features_in_tile(mode="viz", viz_sampling="low", **params))
    tile_viz_med = list(space.features_in_tile(mode="viz", viz_sampling="med", **params))
    tile_viz_high = list(
        space.features_in_tile(mode="viz", viz_sampling="high", **params)
    )

    len_viz_off = len(tile_viz_off)
    len_viz_low = len(tile_viz_low)
    len_viz_med = len(tile_viz_med)
    len_viz_high = len(tile_viz_high)
    assert len_viz_off >= len_viz_low > len_viz_med >= len_viz_high
