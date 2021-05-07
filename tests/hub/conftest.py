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

"""Module for providing test fixtures for the Hub API tests."""

from time import sleep

import pytest

from xyzspaces.apis import HubApi
from xyzspaces.config.default import XYZConfig
from xyzspaces.datasets import get_chicago_parks_data, get_countries_data


@pytest.fixture()
def api():
    """Create shared XYZ Hub Api instance as a pytest fixture."""
    api = HubApi(config=XYZConfig.from_default())
    return api


@pytest.fixture()
def space_id():
    """Create shared XYZ space with countries data as a pytest fixture."""
    api = HubApi(config=XYZConfig.from_default())

    # setup, create temporary space
    res = api.post_space(
        data={
            "title": "Testing xyzspaces",
            "description": "Temporary space containing countries data.",
        }
    )
    space_id = res["id"]

    # add features to space
    gj_countries = get_countries_data()
    sleep(0.5)
    api.put_space_features(space_id=space_id, data=gj_countries)

    yield space_id

    # now teardown (delete temporary space)
    api.delete_space(space_id=space_id)


@pytest.fixture()
def point_space_id():
    """Create shared XYZ space with Chicago Parks data."""
    api = HubApi(config=XYZConfig.from_default())
    # setup, create temporary space
    res = api.post_space(
        data={
            "title": "Testing xyzspaces",
            "description": "Temporary space containing Chicago Parks data",
        }
    )
    space_id = res["id"]
    gj_chicago_parks = get_chicago_parks_data()
    sleep(0.5)
    api.put_space_features(space_id=space_id, data=gj_chicago_parks)
    yield space_id

    # now teardown (delete temporary space)
    api.delete_space(space_id=space_id)
