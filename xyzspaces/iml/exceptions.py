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
"""This module defines all the exceptions for iml package."""


class AuthenticationException(Exception):
    """
    This ``AuthenticationException`` is raised either authentication
    or authorization on the platform fails.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self) -> str:
        """
        Return the message to be raised for this exception.

        :return: error message
        """
        return """An error occurred during authentication or authorization with HERE
                    platform: Status {status} -
                    Reason {reason}\n Response: {body}""".format(
            status=self.resp.status_code,
            reason=self.resp.reason,
            body=self.resp.text,
        )


class TooManyRequestsException(Exception):
    """Exception raised for API HTTP response status code 429.

    This is a dedicated exception to be used with the `backoff` package, because
    it requires a specific exception class.
    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the response status code, reason and text
        content, separated with commas.
        """

        return "TooManyRequestsException: Status \
                {status} - Reason {reason}\n\n" "Response: {body}".format(
            status=self.resp.status_code,
            reason=self.resp.reason,
            body=self.resp.text,
        )


class ConfigException(Exception):
    """
    This ``ConfigException`` is raised whenever there is any error related to
    platform configuration.
    """


class PayloadTooLargeException(Exception):
    """Exception raised for API HTTP response status code 513.

    This is a dedicated exception to be used for interactive map layer.
    This exception will be raised when response payload is larger than the
    specified limits of the interactive map layer.
    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the response status code, reason and text
        content, separated with commas.
        """

        return (
            "PayloadTooLargeException: Status \
                {status} - Reason {reason}\n\n"
            "Response: {body}".format(
                status=self.resp.status_code, reason=self.resp.reason, body=self.resp.text
            )
        )


class RequestEntityTooLargeException(Exception):
    """Exception raised for API HTTP response status code 413.

    This is a dedicated exception to be used for interactive map layer.
    This exception will be raised when request body is larger than the
    specified limits of the interactive map layer.
    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the response status code, reason and text
        content, separated with commas.
        """

        return (
            "RequestEntityTooLargeException: Status \
                {status} - Reason {reason}\n\n"
            "Response: {body}".format(
                status=self.resp.status_code, reason=self.resp.reason, body=self.resp.text
            )
        )
