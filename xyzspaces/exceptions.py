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

"""This module defines API exceptions."""


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""

    pass


class ApiError(Exception):
    """Exception raised for API HTTP response status codes not in [200...300).

    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.

    Example:

    >>> try:
    >>>     import os
    >>>     os.environ["XYZ_TOKEN"] = "MY-XYZ-TOKEN"
    >>>     api = HubApi()
    >>>     api.get("/hub/nope").json()
    >>> except ApiError as e:
    >>>     resp = e.value.args[0]
    >>>     if resp.status_code == 404 and resp.reason == "Not Found":
    >>>         ...
    """

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the repsonse's status code, reason and text
        content, separated with commas.
        """
        resp = self.args[0]
        return f"{resp.status_code}, {resp.reason}, {resp.text}"


class TooManyRequestsException(Exception):
    """Exception raised for API HTTP response status code 429.

    This is a dedicated exception to be used with the `backoff` package, because
    it requires a specific exception class.

    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.
    """

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the repsonse's status code, reason and text
        content, separated with commas.
        """
        resp = self.args[0]
        return f"{resp.status_code}, {resp.reason}, {resp.text}"
