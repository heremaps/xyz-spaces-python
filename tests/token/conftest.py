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

"""Module for providing test fixtures for the Token API tests."""

import os
import warnings

import pytest

from xyzspaces.apis import TokenApi
from xyzspaces.exceptions import AuthenticationError

HERE_USER = os.environ.get("HERE_USER")
HERE_PASSWORD = os.environ.get("HERE_PASSWORD")


@pytest.fixture()
def api():
    """Create shared XYZ Token API instance as a pytest fixture."""
    credentials = {"username": HERE_USER, "password": HERE_PASSWORD}
    try:
        api = TokenApi(credentials=credentials)
    except AuthenticationError:
        api = TokenApi()
        warnings.warn(
            "Ignoring invalid credentials, creating TokenApi "
            "instance without. Access limitations may apply."
        )
    return api
