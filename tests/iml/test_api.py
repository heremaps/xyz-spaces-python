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
"""Test api module."""
import pytest

from tests.iml.conftest import get_mock_response
from xyzspaces.iml.apis.api import Api
from xyzspaces.iml.exceptions import (
    AuthenticationException,
    PayloadTooLargeException,
    RequestEntityTooLargeException,
    TooManyRequestsException,
)


def test_raise_response_exception():
    reason = "This is mock reason"
    text = "This is mock text"
    mock_response = get_mock_response(513, reason, text)
    with pytest.raises(PayloadTooLargeException):
        Api.raise_response_exception(mock_response)

    mock_response = get_mock_response(401, reason, text)
    with pytest.raises(AuthenticationException):
        Api.raise_response_exception(mock_response)

    mock_response = get_mock_response(413, reason, text)
    with pytest.raises(RequestEntityTooLargeException):
        Api.raise_response_exception(mock_response)

    mock_response = get_mock_response(400, reason, text)
    with pytest.raises(Exception):
        Api.raise_response_exception(mock_response)

    mock_response = get_mock_response(429, reason, text)
    with pytest.raises(TooManyRequestsException):
        Api.raise_response_exception(mock_response)
