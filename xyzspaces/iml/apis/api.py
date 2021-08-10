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
This module implements base class for low level api client.
"""
import urllib.request
from typing import Any, Dict, Optional, Union

import requests

from xyzspaces.iml.exceptions import (
    AuthenticationException,
    PayloadTooLargeException,
    RequestEntityTooLargeException,
    TooManyRequestsException,
)


class Api:
    """Base class for low level api calls."""

    def __init__(self, access_token, proxies: Optional[dict] = None):
        self.access_token = access_token
        self._user_agent = "dhpy"
        self.proxies: Optional[Dict[Any, Any]] = proxies or urllib.request.getproxies()

    @property
    def headers(self) -> dict:
        """
        Return HTTP request headers with Bearer token in ``Authorization``
        field.

        :return: authorization tokens
        """
        return {"Authorization": f"Bearer {self.access_token}"}

    def get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a get request of an API at a specified URL with backoff.

        :param url: URL of the API.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the Api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """

        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        return requests.get(
            url, headers=headers, params=params, proxies=self.proxies, **kwargs
        )

    def head(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a head request of an API at specified URL.

        :param url: URL of the API.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """
        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        return requests.head(
            url, headers=headers, params=params, proxies=self.proxies, **kwargs
        )

    def post(
        self,
        url: str,
        data: Optional[Union[dict, list, bytes, str]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a post request of an API at a specified URL with backoff.

        :param url: URL of the API.
        :param data: Post data for http request.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """
        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        if isinstance(data, dict) or isinstance(data, list):
            return requests.post(
                url,
                headers=headers,
                json=data,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )
        else:
            return requests.post(
                url,
                headers=headers,
                data=data,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )

    def put(
        self,
        url: str,
        data: Optional[Union[dict, bytes]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a put request of an API at a specified URL with backoff.

        :param url: URL of the API
        :param data: Put data for http request.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """
        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        if isinstance(data, dict):
            return requests.put(
                url,
                json=data,
                headers=headers,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )
        else:
            return requests.put(
                url,
                data=data,
                headers=headers,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )

    def patch(
        self,
        url: str,
        data: Optional[Union[dict, bytes, str]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a patch request of an API at a specified URL with backoff.

        :param url: URL of the API
        :param data: Patch data for http request.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """
        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        if isinstance(data, dict) or isinstance(data, list):
            return requests.patch(
                url,
                headers=headers,
                json=data,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )
        else:
            return requests.patch(
                url,
                headers=headers,
                data=data,
                params=params,
                proxies=self.proxies,
                **kwargs,
            )

    def delete(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Perform a delete request of an API at a specified URL with backoff.

        :param url: URL of the API
        :param params: parameters to pass to the API.
        :param headers: Request headers. Defaults to the api headers property.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        """
        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        return requests.delete(
            url, headers=headers, params=params, proxies=self.proxies, **kwargs
        )

    @staticmethod
    def raise_response_exception(resp: requests.Response) -> None:
        """
        Parse HTTP errors status code and raise necessary exceptions.

        :param resp: An HTTP response to parse.
        :raises TooManyRequestsException: If platform responds with HTTP 429.
        :raises AuthenticationException: If platform responds with HTTP 401 or 403.
        :raises RequestEntityTooLargeException: If platform responds with HTTP 413.
        :raises PayloadTooLargeException: If platform responds with HTTP 513.
        :raises Exception: If client responds with any other exception.
        """
        if resp.status_code == 429:
            raise TooManyRequestsException(resp)
        elif resp.status_code in [401, 403]:
            raise AuthenticationException(resp)
        elif resp.status_code == 413:
            raise RequestEntityTooLargeException(resp)
        elif resp.status_code == 513:
            raise PayloadTooLargeException(resp)
        else:
            raise Exception(resp.text)
