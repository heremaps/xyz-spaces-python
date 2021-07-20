# Copyright (C) 2020-2021 HERE Global B.V. and its affiliate(s).
# All rights reserved.
#
# This software and other materials contain proprietary information
# controlled by HERE and are protected by applicable copyright legislation.
# Any use and utilization of this software and other materials and
# disclosure to any third parties is conditional upon having a separate
# agreement with HERE for the access, use, utilization or disclosure of this
# software. In the absence of such agreement, the use of the software is not
# allowed.

"""
This module contains an :class:`AAAOauth2ApiClient` class to perform oauth API operations.

The HERE API reference documentation used in this module can be found here:
|iam_api_reference|

.. |iam_api_reference| raw:: html

   <a href="https://developer.here.com/documentation/identity-access-management/api-reference-swagger.html">IAM API Reference</a>  # noqa
"""

from typing import Dict, Optional

from requests_oauthlib import OAuth1

from xyzspaces.iml.apis.api import Api
from xyzspaces.iml.exceptions import AuthenticationException, TooManyRequestsException


class AAAOauth2Api(Api):
    """
    This class provides access to HERE platform AAA Oauth2 APIs.
    """

    def __init__(
        self,
        base_url: str,
        proxies: Optional[dict] = None,
    ):
        """
        Instantiate API with auth token.

        :param proxies: an optional proxy configuration. Defaults to the environment proxy
        configuration.
        """
        self.base_url = base_url
        self.proxies = proxies
        super().__init__(
            access_token=None,
            proxies=self.proxies,
        )

    def request_scoped_access_token(self, oauth: OAuth1, data: str) -> Dict:
        """
        Request scoped access oauth2 token from platform.

        :param oauth: oauth1 configuration.
        :param data: a string which represents request body.
        :return: a json with scoped access token.
        :raises TooManyRequestsException: If the status code of the HTTP response is 429
        :raises AuthenticationException: If platform responds with HTTP 401 or 403.
        :raises RuntimeError: If platform does not respond with HTTP 200.
        """
        resp = self.post(
            url=self.base_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
            auth=oauth,
        )
        if resp.status_code == 429:
            raise TooManyRequestsException(resp)
        elif resp.status_code in [401, 403]:
            raise AuthenticationException(resp)
        elif resp.status_code != 200:
            raise RuntimeError(
                "Authentication returned unexpected status {}".format(resp.status_code)
            )
        resp_dict: dict = resp.json()
        return resp_dict
