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

"""Module for providing test fixtures for the IML tests."""

import os
from collections import namedtuple

import pytest

from xyzspaces import IML

HERE_USER_ID = os.environ.get("HERE_USER_ID")
HERE_CLIENT_ID = os.environ.get("HERE_CLIENT_ID")
HERE_ACCESS_KEY_ID = os.environ.get("HERE_ACCESS_KEY_ID")
HERE_ACCESS_KEY_SECRET = os.environ.get("HERE_ACCESS_KEY_SECRET")


@pytest.fixture()
def read_layer():
    """Fixture for all read operations on interactive map layer."""
    iml = IML.from_catalog_hrn_and_layer_id(
        catalog_hrn="hrn:here:data::olp-here:catalog-to-test-in-ci-don-not-delete",
        layer_id="countries",
    )
    return iml.layer


def env_setup_done():
    env_vars_present = all(
        v is not None
        for v in [
            HERE_USER_ID,
            HERE_CLIENT_ID,
            HERE_ACCESS_KEY_ID,
            HERE_ACCESS_KEY_SECRET,
        ]
    )
    return env_vars_present


def get_mock_response(status_code: int, reason: str, text: str):
    """
    Return mock response.

    :param status_code: An int representing status_code.
    :param reason: A string to represent reason.
    :param text: A string to represent text.
    :return: MockResponse object.
    """
    MockResponse = namedtuple("MockResponse", ["status_code", "reason", "text"])
    mock_response = MockResponse(status_code, reason, text)
    return mock_response
