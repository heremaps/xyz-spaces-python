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

"""Module for testing various HTTP method aliases."""

import pytest

from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_alias(api, space_id):
    """Get space statistics."""
    path = f"/hub/spaces/{space_id}/statistics"
    stats = api.get(path=path).json()
    assert stats["type"] == "StatisticsResponse"
