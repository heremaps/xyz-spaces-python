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

"""This module configures logging."""

import json
import logging
import logging.config
import os


def setup_logging(
    default_path: str = "config/logconfig.json",
    default_level: int = logging.ERROR,
    env_key: str = "XYZ_LOG_CONFIG",
):
    """Set up logging configuration.

    :param default_path: A string representing the path of the config file in JSON format.
    :param default_level: An int representing logging level.
    :param env_key: A string representing environment variable to enable logging to file.
    """
    path = default_path
    value = os.environ.get(env_key)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s"
            "- %(message)s",
        )


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library


class NullHandler(logging.Handler):
    """NullHandler class is a  'no-op' handler for use by library developers."""

    def emit(self, record):
        """Skip the emit record. This is used to give preference to user."""
        pass


logger = logging.getLogger("xyzspaces")
logger.addHandler(NullHandler())
