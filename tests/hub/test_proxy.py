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

"""Module for testing proxies for the XYZ API class."""

import multiprocessing
import os
import socket
import subprocess
import time
from contextlib import closing

import pytest

from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


def find_free_port():
    """Find and return a free port to use on this machine."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_proxy(port: int):
    """Start a HTTP proxy."""
    cmd = f"proxy.py --port {port}".split()
    subprocess.check_output(cmd)


@pytest.fixture()
def proxy_port():
    """Run an HTTP proxy as a pytest fixture."""
    port = find_free_port()
    p = multiprocessing.Process(target=run_proxy, args=[port])
    p.daemon = True
    p.start()
    time.sleep(1)

    yield port

    # now teardown (terminating temporary proxy)
    p.terminate()
    time.sleep(1)


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_no_proxy(api):
    """Get the hub info with no proxy set."""
    hub = api.get_hub()
    assert "reporter" in hub
    assert "status" in hub
    assert "schemaVersion" in hub


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
@pytest.mark.skipif(
    True,
    reason="Needs to set/use/expose a fixed port on Docker for CI/CD, first...",
)
def test_living_proxy(api, proxy_port):
    """Get the hub info with specified and running proxy."""
    os.environ["HTTP_PROXY"] = f"http://localhost:{proxy_port}"
    os.environ["HTTPS_PROXY"] = f"https://localhost:{proxy_port}"
    try:
        hub = api.get_hub()
    finally:
        del os.environ["HTTP_PROXY"]
        del os.environ["HTTPS_PROXY"]
    assert "reporter" in hub
    assert "status" in hub
    assert "schemaVersion" in hub
