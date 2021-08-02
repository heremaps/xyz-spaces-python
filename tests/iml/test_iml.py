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
"""This module will test functionality in IML class."""

import json
from pathlib import Path
from time import sleep

import pytest

from tests.iml.conftest import env_setup_done
from xyzspaces import IML
from xyzspaces.iml.catalog import Catalog
from xyzspaces.iml.credentials import Credentials
from xyzspaces.iml.layer import InteractiveMapLayer


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_from_catalog_hrn_and_layer_id():
    """Test IML classmethod."""
    hrn = "hrn:here:data::olp-here:catalog-to-test-in-ci-don-not-delete"
    layer_id = "countries"
    iml = IML.from_catalog_hrn_and_layer_id(catalog_hrn=hrn, layer_id=layer_id)
    assert isinstance(iml.catalog, Catalog)
    assert isinstance(iml.layer, InteractiveMapLayer)


@pytest.mark.skipif(not env_setup_done(), reason="Credentials are not setup in env.")
def test_catalog_lifecycle():
    """This funtion tests catalog lifecycle.

    - Create a new catalod and interactive map layer
    - Add features to layer
    - remvoe features from layer
    - update features from layer
    - Delete catalog.
    """
    # cleanup before start. just delete catalg if it already exists.
    cred = Credentials.from_env()
    try:
        obj = IML()
        obj.delete_catalog(
            catalog_hrn="hrn:here:data::olp-here:test-catalog-iml-remove",
            credentials=cred,
        )
        sleep(5)
    except:  # noqa: E722
        pass

    layer_details = {
        "id": "countries-test",
        "name": "countries-test",
        "summary": "Borders of world countries.",
        "description": "Borders of world countries. Test layer for read operations in CI",
        "layerType": "interactivemap",
        "interactiveMapProperties": {},
    }
    iml = IML.new(
        catalog_id="test-catalog-iml-remove",
        catalog_name="test-catalog-iml-remove",
        catalog_summary="This is test catalog used in CI for xyzspaces.",
        catalog_description="Test IML functionality in CI for xyzspaces.",
        layer_details=layer_details,
        credentials=cred,
    )
    sleep(2)
    root = Path(__file__).parent.parent.parent
    file_path = root / Path("xyzspaces") / Path("datasets") / Path("countries.geo.json")
    iml.layer.write_features(from_file=file_path)
    assert iml.layer.statistics["count"]["value"] == 179
    feature = {
        "geometry": {"coordinates": [73, 19], "type": "Point"},
        "properties": {},
        "type": "Feature",
        "id": "test-delete",
    }
    iml.layer.write_feature(feature_id="test-delete", data=feature)
    sleep(1)
    resp = iml.layer.get_feature(feature_id="test-delete")
    ft = resp.to_geojson()
    assert ft["id"] == "test-delete"
    feature["properties"] = {"name": "delete"}
    iml.layer.update_feature(feature_id="test-delete", data=feature)
    sleep(1)
    iml.layer.delete_feature(feature_id="test-delete")
    # Add new layer to the catalog.
    layer2 = {
        "id": "countries-test2",
        "name": "countries-test2",
        "summary": "Borders of world countries second layer.",
        "description": "Borders of world countries.",
        "layerType": "interactivemap",
        "interactiveMapProperties": {},
    }
    iml.add_interactive_map_layer(
        catalog_hrn="hrn:here:data::olp-here:test-catalog-iml-remove",
        layer_details=layer2,
        credentials=cred,
    )
    assert iml.layer.id == "countries-test2"
    with open(file_path) as fh:
        countries_data = json.load(fh)
    iml.layer.write_features(features=countries_data)
    assert iml.layer.statistics["count"]["value"] == 179
    resp = iml.layer.get_features(feature_ids=["IND", "USA", "DEU"])
    features = resp.to_geojson()["features"]
    iml.layer.delete_features(feature_ids=["IND", "USA", "DEU"])
    assert iml.layer.statistics["count"]["value"] == 176
    iml.layer.write_features(features=features)
    sleep(0.5)
    assert iml.layer.statistics["count"]["value"] == 179
