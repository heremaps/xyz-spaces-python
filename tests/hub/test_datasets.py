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

"""Module for testing example default datasets."""

from pathlib import Path

import pytest

import xyzspaces
from xyzspaces.datasets import get_countries_data
from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_load_countries():
    """Load countries dataset."""
    gj_countries = get_countries_data()
    keys = gj_countries.keys()
    assert "type" in keys
    assert "features" in keys
    assert len(gj_countries["features"]) == 180

    datasets_home = Path(xyzspaces.datasets.__file__).parent
    url_countries = (
        "https://raw.githubusercontent.com"
        "/johan/world.geo.json/master/countries.geo.json"
    )
    fn_countries = datasets_home / Path(url_countries).name
    try:
        fn_countries.unlink()
    except OSError:
        pass
    assert not fn_countries.exists()

    gj_countries = get_countries_data()
