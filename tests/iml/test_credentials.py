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
"""Test credentials module."""
import tempfile
from pathlib import Path

import pytest

from xyzspaces.iml.credentials import Credentials
from xyzspaces.iml.exceptions import ConfigException


def test_from_credentials_file():
    """Test credentials from file."""
    file_path = (
        Path(__file__).parent / Path("data") / Path("dummy_credentials.properties")
    )
    cred = Credentials.from_credentials_file(file_path)
    assert cred.cred_properties["user"] == "dummy_user_id"
    assert cred.cred_properties["client"] == "dummy_client_id"
    assert cred.cred_properties["key"] == "dummy_access_key_id"
    assert cred.cred_properties["secret"] == "dummy_access_key_secret"
    assert cred.cred_properties["endpoint"] == "dummy_token_endpoint"
    with pytest.raises(ConfigException):
        with tempfile.NamedTemporaryFile() as tmp:
            _ = Credentials.from_credentials_file(tmp.name)
