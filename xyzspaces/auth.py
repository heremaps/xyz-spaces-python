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
This module provides HERE authentication via cookies for the Token API.

This :func:`get_auth_cookies()` function simulates the login process on
http://developer.here.com to obtain an access cookie for authenticating
with certain RESTful APIs like the XYZ Token API.

This implementation is inspired by the Open Source HERE XYZ CLI:
https://github.com/heremaps/here-cli/blob/master/src/sso.ts.
"""

import requests

from .exceptions import AuthenticationError

URL = (
    "https://account.here.com/sign-in?"
    "client-id=es1HEn2LGqFocvfD1eEt&version=3&sdk=true&type=frame&"
    "uri=https%3A%2F%2Fxyz.here.com&sign-in-screen-config=password,"
    "heread&track-id=trackUPMUI&lang=en-us"
)
SIGN_IN_URL = "https://account.here.com/api/account/sign-in-with-password"


def filter_cookies(cookies: requests.cookies.RequestsCookieJar, prefix: str) -> dict:
    """
    Filter :mod:`requests` cookies with some given name prefix into a new dict.

    :param cookies: A :mod:`requests` cookies object.
    :param prefix: A prefix string to search in cookies.
    :return: A dict.

    Example:

    Input::

        <RequestsCookieJar[
            <Cookie locale=en-US for .here.com/>,
            <Cookie here_account=foobar for account.here.com/>,
            <Cookie here_account.sig=barfoo for account.here.com/>]
        >

    Output::

        {'here_account': 'foobar', 'here_account.sig': 'barfoo'}
    """
    return {k: v.split(";")[0] for (k, v) in cookies.items() if k.startswith(prefix)}


def get_auth_cookies(username: str, password: str) -> dict:
    """Get authentication cookies from name and password of a HERE account.

    :param username: Username for HERE account.
    :param password: Password for HERE account.
    :return: A dict.
    :raises AuthenticationError: If status_code for HTTP response returned by
                                 :mod:`requests` is not equal to 200.
    """
    resp1 = requests.get(URL)
    body = resp1.text
    csrf_token = body[body.find("csrf") :]
    csrf_token = csrf_token[csrf_token.find(":") + 3 : csrf_token.find(",") - 1]
    headers = {"x-csrf-token": csrf_token}
    request_body = {
        "realm": "here",
        "email": username,
        "password": password,
        "rememberMe": True,
    }
    here_cookies = filter_cookies(resp1.cookies, prefix="here")
    resp2 = requests.post(
        SIGN_IN_URL, headers=headers, json=request_body, cookies=here_cookies
    )
    if resp2.status_code != 200:
        raise AuthenticationError(
            "Error while authenticating. " "Please check credentials and try again."
        )
    here_cookies = filter_cookies(resp2.cookies, prefix="here")
    return here_cookies
