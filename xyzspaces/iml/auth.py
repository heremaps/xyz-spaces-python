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
This module provides an ``Auth`` class to authenticate an app on the platform.

The authentication is based on some credentials object and will create an
access token. It can be checked if the token is still valid, and it can be
refreshed, too.
"""


from datetime import datetime, timedelta
from typing import Optional

from requests_oauthlib import OAuth1

from xyzspaces.iml.apis.aaa_oauth2_api import AAAOauth2Api
from xyzspaces.iml.credentials import Credentials


class Auth:
    """
    This class is responsible for authenticating with the HERE platform.

    It requires PlatformCredentials, AAAOauth2BaseApi object.
    """

    def __init__(self, credentials: Credentials, aaa_oauth2_api: AAAOauth2Api):
        """
        Instantiate authentication token.

        :param credentials: an instance of PlatformCredentials
        :param aaa_oauth2_api: an instance of AAAOauth2Api required
            in case of Credentials type.
        """
        self.credentials = credentials
        self.aaa_oauth2_api = aaa_oauth2_api

        self._token: Optional[str] = None
        self._token_type: Optional[str] = None
        self._token_expires_in: Optional[int] = None
        self._token_requested_at: Optional[datetime] = None
        self._token_expires_at: Optional[datetime] = None
        self._scope: Optional[str] = None

    @property
    def token(self) -> Optional[str]:
        """
        Return the current token or requests a new one if needed.

        :return: a valid token
        """
        if not self.token_still_valid():
            self.generate_token()
        return self._token

    def token_still_valid(self) -> bool:
        """
        Check whether the auth token is still valid or expired.

        :return: a boolean indicating if a token is still valid.
        """
        if not self._token or not self._token_expires_at:
            return False
        return datetime.now() < (self._token_expires_at - timedelta(seconds=60))

    def generate_token(self):
        """
        Authenticate with the HERE account service and retrieve a new token.
        """
        oauth = OAuth1(
            self.credentials.cred_properties["key"],
            client_secret=self.credentials.cred_properties["secret"],
            signature_method="HMAC-SHA256",
        )
        response_json = self.aaa_oauth2_api.request_scoped_access_token(
            oauth, data="grant_type=client_credentials"
        )

        self._token = response_json.get("access_token")
        self._token_type = response_json.get("token_type")
        self._token_expires_in = int(response_json.get("expires_in"))
        self._token_requested_at = datetime.now()
        self._token_expires_at = self._token_requested_at + timedelta(
            seconds=self._token_expires_in
        )
