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
Module for testing xyzspaces.utils.

Here we don't generate any temporary spaces.
"""

import os

import pytest

from xyzspaces.utils import get_xyz_token, join_string_lists

XYZ_TOKEN = get_xyz_token()


def test_join_string_lists():
    """Test join_string_lists function."""
    res = join_string_lists(foo=["a", "b", "c"], bar=["a", "b"], foobar=None)
    assert res == {"foo": "a,b,c", "bar": "a,b"}


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_xyz_token_empty():
    """Test for empty xyz_token."""
    # storing existing token into variable.
    token = os.environ["XYZ_TOKEN"]
    del os.environ["XYZ_TOKEN"]
    result = get_xyz_token()
    assert result == ""
    # resetting the token again.
    os.environ["XYZ_TOKEN"] = token
