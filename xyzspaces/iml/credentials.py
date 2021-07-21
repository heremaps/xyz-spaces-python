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
This module provides a ``Credentials`` class to be used for authentication.

A credentials object can be created from a ``credentials.properties`` file obtained
from the HERE platform portal or from environment variables.
"""

from os import getenv
from os.path import expanduser, expandvars
from typing import List

from pyhocon import ConfigFactory, ConfigMissingException, ConfigTree

from xyzspaces.iml.exceptions import ConfigException

DEFAULT_CREDENTIALS_PATH = "~/.here/credentials.properties"


class Credentials:
    """
    Credentials provides functions for dealing with the HERE platform
    Credentials.

    Credentials can be read from the following locations:

    - The default location: "~/.here/credentials.properties"
    - A custom path to a credentials properties file
    - Environment variables
    """

    def __init__(
        self,
        cred_properties: ConfigTree,
    ):
        """
        Instantiate the credentials object.

        :param cred_properties: the properties of Credentials.
        """
        self.cred_properties = cred_properties

    @classmethod
    def from_default(cls) -> "Credentials":
        """Return the credentials object from the default default credential
        path at '~/.here/credentials.properties'.

        If environmental variables are set, these values will override the ones
        found in the default file.

        If no default file is found, this method will try to read the
        credentials from the environmental variables.

        :return: credentials
        """

        try:
            credentials = cls.from_credentials_file(DEFAULT_CREDENTIALS_PATH)
        except (ConfigException, FileNotFoundError):
            credentials = cls.from_env()

        credentials.patch_using_env()
        return credentials

    @classmethod
    def from_credentials_file(cls, path: str) -> "Credentials":
        """
        Return the credentials object from a specified credentials path.

        :param path: path to a HERE platform credentials.properties file.
        :return: credentials
        :raises ConfigException: Erroneous credentials.properties file in path

        """
        credentials_path = expanduser(expandvars(path))
        try:
            credentials_properties = ConfigFactory.parse_file(credentials_path)
            user = credentials_properties.get("here.user.id")
            client = credentials_properties["here.client.id"]
            key = credentials_properties["here.access.key.id"]
            secret = credentials_properties["here.access.key.secret"]
            endpoint = credentials_properties["here.token.endpoint.url"]
            if user and client and key and secret and endpoint:
                credentials_config = ConfigTree()
                credentials_config.put("user", user)
                credentials_config.put("client", client)
                credentials_config.put("key", key)
                credentials_config.put("secret", secret)
                credentials_config.put("endpoint", endpoint)
                return Credentials(credentials_config)
            else:
                raise ConfigException("Erroneous ", credentials_path, " file")
        except ConfigMissingException:
            raise ConfigException("Erroneous ", credentials_path, " file")

    @classmethod
    def from_env(cls) -> "Credentials":
        """
        Return the credentials object from the following environment variables:

          - ``HERE_USER_ID``
          - ``HERE_CLIENT_ID``
          - ``HERE_ACCESS_KEY_ID``
          - ``HERE_ACCESS_KEY_SECRET``
          - ``HERE_TOKEN_ENDPOINT_URL`` (optional)

        :return: credentials parsed from the environment variables
        :raises ConfigException: missing environmental variables that are mandatory
        """

        user = getenv("HERE_USER_ID")
        client = getenv("HERE_CLIENT_ID")
        access_key_id = getenv("HERE_ACCESS_KEY_ID") or getenv("HERE_ACCESS_KEY")
        access_key_secret = getenv("HERE_ACCESS_KEY_SECRET") or getenv(
            "HERE_ACCESS_SECRET"
        )
        endpoint = (
            getenv("HERE_TOKEN_ENDPOINT_URL")
            or getenv("HERE_TOKEN_ENDPOINT")
            or "https://account.api.here.com/oauth2/token"
        )

        missing_env_vars: List[str] = []

        if not user:
            missing_env_vars.append("HERE_USER_ID")
        if not client:
            missing_env_vars.append("HERE_CLIENT_ID")
        if not access_key_id:
            missing_env_vars.append("HERE_ACCESS_KEY_ID")
        if not access_key_secret:
            missing_env_vars.append("HERE_ACCESS_KEY_SECRET")

        if missing_env_vars:
            raise ConfigException(
                "Missing environmental variables: {}".format(", ".join(missing_env_vars))
            )

        # at this points, we should have all the variables with a non-empty value
        assert user and client and access_key_id and access_key_secret and endpoint

        credentials_config = ConfigTree()
        credentials_config.put("user", user)
        credentials_config.put("client", client)
        credentials_config.put("key", access_key_id)
        credentials_config.put("secret", access_key_secret)
        credentials_config.put("endpoint", endpoint)
        return cls(credentials_config)

    def patch_using_env(self):
        """
        Patch the credentials by reading the following environment variables and
        applying them accordingly.

          - ``HERE_USER_ID``
          - ``HERE_CLIENT_ID``
          - ``HERE_ACCESS_KEY_ID``
          - ``HERE_ACCESS_KEY_SECRET``
          - ``HERE_TOKEN_ENDPOINT_URL``

        Whenever such an environment variable is set,
        it overrides the one loaded from file.
        """
        if self.cred_properties:
            credentials_config = self.cred_properties

            user = getenv("HERE_USER_ID") or credentials_config["user"]
            client = getenv("HERE_CLIENT_ID") or credentials_config["client"]
            key = (
                getenv("HERE_ACCESS_KEY_ID")
                or getenv("HERE_ACCESS_KEY")
                or credentials_config["key"]
            )
            secret = (
                getenv("HERE_ACCESS_KEY_SECRET")
                or getenv("HERE_ACCESS_SECRET")
                or credentials_config["secret"]
            )
            endpoint = (
                getenv("HERE_TOKEN_ENDPOINT_URL")
                or getenv("HERE_TOKEN_ENDPOINT")
                or credentials_config["endpoint"]
            )
            credentials_config["user"] = user
            credentials_config["client"] = client
            credentials_config["key"] = key
            credentials_config["secret"] = secret
            credentials_config["endpoint"] = endpoint
