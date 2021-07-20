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
Module for testing xyzspaces.curl.

Here we don't generate any temporary spaces.
"""

import datetime
import subprocess

import pytest
import requests

import xyzspaces.curl as curl

try:
    subprocess.check_output(["which", "curl"])
    HAVE_CURL = True
except subprocess.CalledProcessError:
    HAVE_CURL = False


@pytest.mark.skipif(False, reason="Not yet implemented.")
@pytest.mark.skipif(not HAVE_CURL, reason="No curl command found.")
def test_new_curl_command_list():
    """Test compare results for new curl command vs. requests using same interface."""
    url = "https://xkcd.com/552/info.0.json"
    curl_cmd = curl.get(url=url)
    curl_res = curl.execute(curl_cmd)
    reqs_res = requests.get(url=url)
    assert curl_res.ok == reqs_res.ok
    assert curl_res.content == reqs_res.content
    resp = curl.execute(["dummy"])
    assert resp.status_code == 500
    assert not resp.content


def test_curl_command_str():
    """Test building curl command as string."""
    cmd = curl.get(url="https://xkcd.com/552/info.0.json")
    assert " ".join(cmd) == "curl --request GET https://xkcd.com/552/info.0.json"


def test_curl_command_list():
    """Test building curl command as list."""
    cmd = curl.get(url="https://xkcd.com/552/info.0.json")
    assert cmd == [
        "curl",
        "--request",
        "GET",
        "https://xkcd.com/552/info.0.json",
    ]


def test_curl_command_data_params():
    """Test building curl command for parameters data and proxy."""
    cmd = curl.post(
        url="https://xkcd.com/552/info.0.json",
        data={"dummy": 2, "type": "test"},
        headers={"Date": datetime.datetime.today().strftime("%Y-%m-%d")},
        proxies={"proxy1": "http://user:password@example.proxy.here.com" ":8888"},
    )
    assert cmd == [
        "curl",
        "--request",
        "POST",
        "https://xkcd.com/552/info.0.json",
        "--header",
        f'Date: {datetime.datetime.today().strftime("%Y-%m-%d")}',
        "--header",
        "Content-Type: application/x-www-form-urlencoded",
        "--data",
        "dummy=2&type=test",
        "--proxy",
        "http://user:password@example.proxy.here.com:8888",
    ]
