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
"""Test all exceptions."""


import pytest

from tests.iml.conftest import get_mock_response
from xyzspaces.iml.exceptions import (
    AuthenticationException,
    PayloadTooLargeException,
    RequestEntityTooLargeException,
    TooManyRequestsException,
)


def test_authentication_exception():
    """Test :class:`AuthenticationException`"""
    status_code = 401
    reason = "This is mock reason"
    text = "This is mock text"
    mock_response = get_mock_response(status_code, reason, text)
    with pytest.raises(AuthenticationException) as execinfo:
        raise AuthenticationException(mock_response)
    resp = execinfo.value.args[0]
    assert resp.status_code == status_code
    assert resp.reason == reason
    assert resp.text == text


def test_payload_too_large_exception():
    """Test :class:`PayloadTooLargeException`"""
    status_code = 513
    reason = "This is mock reason"
    text = "This is mock text"
    mock_response = get_mock_response(status_code, reason, text)
    with pytest.raises(PayloadTooLargeException) as execinfo:
        raise PayloadTooLargeException(mock_response)
    resp = execinfo.value.args[0]
    assert resp.status_code == status_code
    assert resp.reason == reason
    assert resp.text == text


def test_too_many_requests_exception():
    """Test :class:`TooManyRequestsException`"""
    status_code = 429
    reason = "This is mock reason"
    text = "This is mock text"
    mock_response = get_mock_response(status_code, reason, text)
    with pytest.raises(TooManyRequestsException) as execinfo:
        raise TooManyRequestsException(mock_response)
    resp = execinfo.value.args[0]
    assert resp.status_code == status_code
    assert resp.reason == reason
    assert resp.text == text


def test_request_entity_too_large_exception():
    """Test :class:`RequestEntityTooLargeException`"""
    status_code = 413
    reason = "This is mock reason"
    text = "This is mock text"
    mock_response = get_mock_response(status_code, reason, text)
    with pytest.raises(RequestEntityTooLargeException) as execinfo:
        raise RequestEntityTooLargeException(mock_response)
    resp = execinfo.value.args[0]
    assert resp.status_code == status_code
    assert resp.reason == reason
    assert resp.text == text
