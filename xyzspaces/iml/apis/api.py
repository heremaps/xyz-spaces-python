"""
This module implements base class for low level api client.
"""
import urllib.request
from typing import Dict, Optional, Union

import requests
from requests import Response

from xyzspaces.iml.exceptions import AuthenticationException, TooManyRequestsException


class Api:
    """Base class for low level api calls."""

    def __init__(self, access_token, proxies: Optional[dict] = None):
        self.access_token = access_token
        self._user_agent = "dhpy"
        self.proxies = proxies or urllib.request.getproxies()

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
        as_json: bool = True,
        **kwargs,
    ) -> Union[Dict, Response]:
        """
        Perform a get request of an API at a specified URL with backoff.

        :param url: URL of the API.
        :param params: Parameters to pass to the API.
        :param headers: Request headers. Defaults to the Api headers property.
        :param as_json: A boolean to indicate type of response. If `True` then response
            will be returned in json format.
        :param kwargs: Optional arguments that request takes.
        :return: response from the API.
        :raises TooManyRequestsException: If the status code of the HTTP response is 429
        :raises AuthenticationException: If platform responds with HTTP 401 or 403.
        """

        headers = headers or self.headers
        headers["User-Agent"] = self._user_agent
        resp = requests.get(
            url, headers=headers, params=params, proxies=self.proxies, **kwargs
        )
        if resp.status_code == 429:
            raise TooManyRequestsException(resp)
        elif resp.status_code in [401, 403]:
            raise AuthenticationException(resp)
        return resp.json() if as_json else resp

    def head(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> Response:
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
    ) -> Response:
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
    ) -> Response:
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
    ) -> Response:
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
    ) -> Response:
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
