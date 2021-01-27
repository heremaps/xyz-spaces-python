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

"""This package provides access to some public datasets used."""

import json
import warnings
from pathlib import Path

import requests

from xyzspaces import Space

MICROSOFT_BUILDINGS_SPACE_ID = "R4QDHvd1"


def get_countries_data():
    """Pull countries example GeoJSON from the net or a locally cached file.

    If this is not locally cached, yet, it will be after the first call,
    unless the file cannot be saved, in which case it will be re-downloaded
    again with every call.

    Source (under http://unlicense.org):
    https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json

    The data contains 180 countries, and does not cover all existing countries,
    ca. 200. For example the Vatican is missing.

    :return: A JSON object.
    """
    datasets_home = Path(__file__).parent
    url_countries = (
        "https://raw.githubusercontent.com"
        "/johan/world.geo.json/master/countries.geo.json"
    )
    fn_countries = datasets_home / Path(url_countries).name
    if fn_countries.exists():
        gj_countries = json.load(fn_countries.open())
    else:
        gj_countries = requests.get(url_countries).json()
        try:
            json.dump(gj_countries, fn_countries.open("w"))
        except IOError:
            warnings.warn(
                f"Could not cache {url_countries} to {datasets_home}. "
                "Check if you have write access. Will re-download next time."
            )

    # Clean data for this specific file (simply remove features with ID "-99".)
    # gj_countries = [f for f in gj_countries["features"] if f["id"] != "-99"]

    # Clean data to replace non-unique IDs (-99 appears twice) with new ones:
    for f in gj_countries["features"]:
        if f["id"] == "-99":
            name = f["properties"]["name"]
            if name == "Northern Cyprus":
                f["id"] = "NCP"
            elif name == "Somaliland":
                f["id"] = "SML"

    return gj_countries


def get_chicago_parks_data():
    """Create GeoJSON from file ``chicago_parks.geo.json`` stored locally."""
    datasets_home = Path(__file__).parent
    chicago_parks = datasets_home / "chicago_parks.geo.json"

    with open(chicago_parks, encoding="utf-8-sig") as json_file:
        chicago_parks_data = json.load(json_file)
    return chicago_parks_data


def get_microsoft_buildings_space():
    """Create a space object for the MS "US Buildings Footprints" dataset.

    The original source for this dataset can be found on
    https://github.com/Microsoft/USBuildingFootprints.

    :return: A space object.
    """
    microsoft_buildings_space = Space.from_id(MICROSOFT_BUILDINGS_SPACE_ID)

    return microsoft_buildings_space
