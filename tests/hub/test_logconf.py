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

"""This module tests logging configuration."""

import os
from pathlib import Path

import pytest

from xyzspaces.exceptions import ApiError
from xyzspaces.logconf import setup_logging


def test_setup_logging_json(api):
    """Test logging setup using json config file."""
    os.environ["XYZ_LOG_CONFIG"] = str(
        Path(__file__).parents[2] / "xyzspaces" / "config" / "logconfig.json"
    )
    setup_logging()
    space_id = "dummy-111"
    with pytest.raises(ApiError):
        api.get_space(space_id=space_id)
    log_path = Path(__file__).parents[2] / "xyz.log"
    assert log_path.exists()
    assert log_path.stat().st_size > 0
    with open(log_path) as fh:
        lines = fh.read()
        assert " - ERROR - status code: 404, response:" in lines
