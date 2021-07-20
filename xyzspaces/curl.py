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

r"""This module contains functionality related to ``curl`` commands.

It provides methods for creating/executing ``curl`` commands which mimic
the ``requests`` signatures.

This module has been mainly designed to be used in the ``Api`` module for
logging purposes.

The ``curl`` module could be also used as stand alone:

Example:

>>> import xyzspaces.curl as curl
>>> command = curl.get(url='https://xkcd.com/552/info.0.json')
['curl', '--request', 'GET', 'https://xkcd.com/552/info.0.json']
>>> curl.execute(command)
b'{"month": "3", "num": 552, "link": "", "year": "2009", "news": "", "safe_title": "Correlation", "transcript": "[[A man is talking to a woman]]\\nMan: I used to think correlation implied causation.\\nMan: Then I took a statistics class.  Now I don\'t.\\nWoman: Sounds like the class helped.\\nMan: Well, maybe.\\n{{Title text: Correlation doesn\'t imply causation, but it does waggle its eyebrows suggestively and gesture furtively while mouthing \'look over there\'.}}", "alt": "Correlation doesn\'t imply causation, but it does waggle its eyebrows suggestively and gesture furtively while mouthing \'look over there\'.", "img": "https://imgs.xkcd.com/comics/correlation.png", "title": "Correlation", "day": "6"}'  # noqa: E501
[...]
"""

import subprocess as sp
from json import dumps as json_dumps
from typing import List, Mapping, Optional
from urllib.parse import urlencode

from requests.models import Response


def get(url, params=None, **kwargs) -> List[str]:
    """Run ``curl`` ``GET`` mimicking the ``requests.get()`` signature.

    This completes a ``curl`` ``GET`` command.

    :param url: The URL of the server including the path.
    :param params: The query string params.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The ``List[str]`` representation of the ``curl`` ``GET`` command.

    Example:

    >>> import xyzspaces.curl as curl
    >>> curl.get(url="https://xkcd.com/552/info.0.json")
    ['curl', '--request', 'GET', 'ttps://xkcd.com/552/info.0.json']
    """
    return command(url, "get", params, **kwargs)


def put(url, data=None, **kwargs) -> List[str]:
    """Run ``curl`` ``PUT`` command mimicking the ``requests.put()`` signature.

    This completes a ``curl`` ``PUT`` command.

    :param url: The URL of the server including the path for the new object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The ``List[str]`` representation of the ``curl`` ``PUT`` command.
    """
    return command(url, "put", data=data, **kwargs)


def patch(url, data=None, **kwargs) -> List[str]:
    """Run ``curl`` ``PATCH`` command mimicking the ``requests.patch()`` signature.

    This completes a ``curl`` ``PATCH`` command.

    :param url: The URL of the server including the path for the new object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The ``List[str]`` representation of the ``curl`` ``PATCH`` command.
    """
    return command(url, "patch", data=data, **kwargs)


def post(url, data=None, json=None, **kwargs) -> List[str]:
    """Run ``curl`` ``POST`` command mimicking the ``requests.post()`` signature.

    This completes a ``curl`` ``POST`` command.

    :param url: The URL of the server including the path for the new object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
    :param json: (optional) json data.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The ``List[str]`` representation of the ``curl`` ``POST`` command.
    """
    return command(url, "post", data=data, json=json, **kwargs)


def delete(url, **kwargs) -> List[str]:
    """Run ``curl`` ``DELETE`` command mimicking the ``requests.delete()`` signature.

    This completes a ``curl`` ``DELETE`` command.

    :param url: The URL of the server including the path.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The ``List[str]`` representation of the ``curl`` ``DELETE`` command.
    """
    return command(url, "delete", **kwargs)


def command(
    url: str,
    method: str,
    params: Optional[dict] = None,
    **kwargs: Optional[Mapping],
) -> List[str]:
    """Return a ``curl`` command equivalent from the params for :mod:`requests`.

    This builds and returns a list of strings representing a ``curl`` command
    that can be directly passed to functions like
    :func:`subprocess.check_output`. When joined with blanks into a single
    string it can also be used for logging or pasting to a terminal.

    To be used like :func:`requests.get`, passing the same params
    for headers, cookies, etc. So the function signature is similar to
    :func:`requests.get`, with additional ``method`` parameter.

    :param url: The URL of the server including the path.
    :param method: The HTTP method name, e.g. "GET", "PUT", etc.
    :param params: The query string params.
    :param kwargs: Further keyword arguments that should match those expected
        by :mod:`requests`.
    :return: The generated ``curl`` command (a list of strings).

    Example:

    >>> import xyzspaces.curl as curl
    >>> curl.command(method="get", url="https://xkcd.com/552/info.0.json")
    ['curl', '--request', 'GET', 'https://xkcd.com/552/info.0.json']
    """
    command = ["curl", "--request", method.upper()]

    if params:
        url += "?" + urlencode(params)

    command += [url]

    cookies = kwargs.get("cookies")
    if cookies:
        command += ' --cookie "%s"' % ";".join(f"{k}={v}" for k, v in cookies.items())

    headers = kwargs.get("headers")
    if headers:
        for k, v in headers.items():
            command += ["--header", f"{k}: {v}"]

    json = kwargs.get("json")
    if json:
        if headers and "Content-Type" not in headers:
            command += ["--header", "Content-Type: application/json"]
        command += ["--data", json_dumps(json)]

    data = kwargs.get("data")
    if data:
        if headers and "Content-Type" not in headers:
            command += [
                "--header",
                "Content-Type: application/x-www-form-urlencoded",
            ]
        command += ["--data", "&".join(f"{k}={v}" for k, v in data.items())]

    proxies = kwargs.get("proxies")
    if proxies:
        for _, v in proxies.items():
            command += ["--proxy", v]

    return command


def execute(command: List[str]) -> Response:
    r"""Execute a ``command`` and create the ``requests.models.Response`` object.

    The Python's ``subprocess`` module will be used for the executing a ``command``.

    In the ``requests.models.Response`` object will be initialized following attributes:
    _content: The response data from the ``stdout``
    status_code: Simplified conversion from the ``subprocess.CompletedProcess.returncode``
    to ``HTTP`` ones 200 ~ 0, 500 ~ >0.

    :param command: The ``curl`` to be executed in the ``List[str]`` type.
    :return: The generated ``requests.models.Response`` object.

    Example:

    >>> import xyzspaces.curl as curl
    >>> command = curl.get(url='https://xkcd.com/552/info.0.json')
    ['curl', '--request', 'GET', 'ttps://xkcd.com/552/info.0.json']
    >>> curl.execute(command)
    b'{"month": "3", "num": 552, "link": "", "year": "2009", "news": "", "safe_title": "Correlation", "transcript": "[[A man is talking to a woman]]\\nMan: I used to think correlation implied causation.\\nMan: Then I took a statistics class.  Now I don\'t.\\nWoman: Sounds like the class helped.\\nMan: Well, maybe.\\n{{Title text: Correlation doesn\'t imply causation, but it does waggle its eyebrows suggestively and gesture furtively while mouthing \'look over there\'.}}", "alt": "Correlation doesn\'t imply causation, but it does waggle its eyebrows suggestively and gesture furtively while mouthing \'look over there\'.", "img": "https://imgs.xkcd.com/comics/correlation.png", "title": "Correlation", "day": "6"}'  # noqa: E501
    [...]
    """
    CurlResponse = type(
        "CurlResponse",
        (Response,),
        {"setcontent": lambda self, content: setattr(self, "_content", content)},
    )
    response = CurlResponse()
    try:
        cp = sp.run(
            command,
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            close_fds=True,
        )
        response.status_code = 200 if cp.returncode == 0 else 500
        response.setcontent(cp.stdout)
    except:  # noqa: E722
        response.status_code = 500

    return response
