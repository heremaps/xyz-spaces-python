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
This module does access the APIs of an XYZ Hub server or HERE Data Hub.

It provides classes like :class:`HubApi`, :class:`ProjectApi`, and
:class:`TokenApi` to interact with the respective XYZ APIs in a programmatic
way.
"""

import copy
import logging
import urllib
import urllib.request
from typing import Any, Dict, Generator, List, Optional, Union

import backoff
import geojson
import requests

import xyzspaces.curl as curl

from .auth import get_auth_cookies
from .config.default import XYZConfig
from .exceptions import ApiError, TooManyRequestsException
from .utils import join_string_lists

logger = logging.getLogger(__name__)

_CLIENT_ID = "dhpy"


class Api:
    """A low-level HTTP RESTful API client.

    This uses :mod:`requests` to make HTTP requests with typical parameters
    and will return the entire response when calling instances directly, or
    when using the aliased HTTP methods like :meth:`Api.get()`,
    :meth:`Api.put()` etc. provided for convenience.

    All these methods like :meth:`Api.get()`, :meth:`Api.put()` etc. will
    raise :class:`ApiError` if the status code of the HTTP response is not
    in the interval [200, 300).

    This class is a base class for concrete HERE XYZ APIs, but can also be
    used outside of that particular context for any RESTful API, maybe
    with slight changes regarding authentication.
    """

    def __init__(self, config: Optional[XYZConfig] = None):
        """Instantiate an :class:`Api` object.

        :param config:
        """
        if config:
            self.xyzconfig = config
        else:
            self.xyzconfig = XYZConfig.from_default()

        self.cookies: Dict[str, str] = {}
        self.headers = self.xyzconfig.config["http_headers"]
        self.curl_command: List[str] = []

    @backoff.on_exception(backoff.expo, TooManyRequestsException)
    def __call__(
        self,
        method: str,
        path: Optional[str] = "",
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        proxies: Optional[Dict] = None,
    ) -> requests.models.Response:
        """Make an API call with parameters passed to :mod:`requests`.

        :param method: The HTTP method name, e.g. "GET", "PUT", etc.
        :param path: The HTTP path to be appended to the :attr:`server` attribute.
        :param params: A dict holding the HTTP query parameters.
        :param headers: A dict holding the HTTP request headers.
        :param cookies: A dict holding the HTTP request cookies.
        :param json: A JSON object (usually a dict) to be passed as request
            body with content-type ``application/json``.
        :param data: A str to be passed as request body with content-type
            ``application/x-www-form-urlencoded``.
        :param proxies: A dict holding the HTTP proxies to be used.
        :return: The HTTP response returned by the :mod:`requests` package.
        :raises ApiError: If the status code of the HTTP response is not in the
             interval [200, 300).
        """
        url = f"{self.xyzconfig.config['url']}{path}"
        curl_method = getattr(curl, method.lower())
        req_method = getattr(requests, method.lower())
        env_proxies = urllib.request.getproxies()

        self.curl_command = curl_method(
            url=url,
            params=params,
            headers=headers or self.headers,
            cookies=cookies or self.cookies,
            proxies=proxies or env_proxies,
            json=json,
            data=data,
        )

        resp = req_method(
            url,
            params=params,
            headers=headers or self.headers,
            cookies=cookies or self.cookies,
            proxies=proxies or env_proxies,
            json=json,
            data=data,
        )
        code = resp.status_code
        curl_logging = (
            f"Curl command: {' '.join(self.curl_command)} "
            + f"Response status code: {code} "
            + f"Response headers: {resp.headers} "
            + f"Response text: {resp.text}"
        )
        if code == 429:
            raise TooManyRequestsException(resp)
        elif not (200 <= code < 300):
            logger.error(
                f"status code: {code}, response: {resp.text}, "
                f"response headers: {resp.headers}"
            )
            raise ApiError(resp)
        logger.debug(curl_logging)
        return resp

    # HTTP method aliases

    def get(self, **kwargs) -> requests.models.Response:
        """Send a HTTP GET request.

        :param kwargs: Keyword arguments passed when sending the HTTP request.
        :return: The HTTP response.
        """
        return self(method="GET", **kwargs)

    def put(self, **kwargs) -> requests.models.Response:
        """Send a HTTP PUT request.

        :param kwargs: Keyword arguments passed when sending the HTTP request.
        :return: The HTTP response.
        """
        return self(method="PUT", **kwargs)

    def patch(self, **kwargs) -> requests.models.Response:
        """Send a HTTP PATCH request.

        :param kwargs: Keyword arguments passed when sending the HTTP request.
        :return: The HTTP response.
        """
        return self(method="PATCH", **kwargs)

    def post(self, **kwargs) -> requests.models.Response:
        """Send a HTTP POST request.

        :param kwargs: Keyword arguments passed when sending the HTTP request.
        :return: The HTTP response.
        """
        return self(method="POST", **kwargs)

    def delete(self, **kwargs) -> requests.models.Response:
        """Send a HTTP DELETE request.

        :param kwargs: Keyword arguments passed when sending the HTTP request.
        :return: The HTTP response.
        """
        return self(method="DELETE", **kwargs)


class ProjectApi(Api):
    """XYZ RESTful Project API abstraction.

    Instances of this class allow to manage XYZ Hub projects.

    API calls must be authenticated via a bearer token which needs to be
    provided in env variable called as ``XYZ_TOKEN`` or in config object
    when initialising an instance.
    """

    def __init__(self, config: Optional[XYZConfig] = None):
        """Instantiate a :class:`ProjectApi` object.

        :param config:
        """
        if config:
            super().__init__(config)
        else:
            super().__init__(XYZConfig.from_default())

        self.headers = copy.deepcopy(self.xyzconfig.config["http_headers"])
        self.headers.pop("Content-Type")

    # Read projects

    def get_projects(
        self,
        paginate: Optional[bool] = None,
        handle: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """List the projects either for the token owner or list the published projects.

        :param paginate: A Boolean telling if the results should be paginated
            (default: ?).
        :param handle: A string to be used when running the next request in
            a sequence of pagninated responses. Works only when ``paginate``
            is ``True``.
        :param limit: The max. number of projects to return.
            Works only when ``paginate`` is ``True``.
        :return: A JSON object containing information about the projects.
        """
        path = "/project-api/projects"
        params: Dict[str, Any] = {}
        # if param paginate is false then api returns all projects.
        if paginate:
            params["paginate"] = "true"
            if handle is not None:
                params["handle"] = handle
            if limit is not None:
                params["limit"] = limit
        else:
            params["paginate"] = "false"
        return self.get(path=path, params=params).json()

    def get_project(self, project_id: str) -> dict:
        """Get the project by ID.

        :param project_id: A string representing the project ID.
        :return: A JSON object with information about the requested project.
        """
        path = f"/project-api/projects/{project_id}"
        return self.get(path=path).json()

    # Edit projects

    def post_project(self, data) -> dict:
        """Create a project.

        :param data: A JSON object describing the project to be created.
        :return: A JSON object with all information about the created project.
        """
        path = "/project-api/projects"
        return self.post(path=path, json=data).json()

    def put_project(self, project_id: str, data) -> dict:
        """Update a project by ID.

        Update the project with the provided project ID and create it if it
        does not exist. This will replace the whole project definition.

        :param project_id: A string representing the desired project ID.
        :param data: A JSON object describing the project details to be updated.
        :return: A JSON object with information about the updated project.
        """
        path = f"/project-api/projects/{project_id}"
        return self.put(path=path, json=data).json()

    def patch_project(self, project_id: str, data) -> dict:
        """Update parts of a project by ID.

        :param project_id: A string representing the desired project ID.
        :param data: A JSON object describing the project parts to be updated.
        :return: A JSON object with information about the updated project.
        """
        path = f"/project-api/projects/{project_id}"
        return self.patch(path=path, json=data).json()

    def delete_project(self, project_id: str) -> str:
        """Delete a project by ID.

        :param project_id: A string representing the desired project ID.
        :return: An empty string if the operation was successful.
        """
        path = f"/project-api/projects/{project_id}"
        return self.delete(path=path).text


class TokenApi(Api):
    """XYZ RESTful Token API abstraction.

    Instances of this API class allow to manage HERE XYZ tokens.

    API calls must be authenticated via authenticated access cookies derived
    from the username and password of an existing HERE developer account with
    access to HERE XYZ. These need to be provided as a ``credentials``
    parameter when initialising an instance.

    Example:

    >>> from xyzspaces.apis import TokenApi
    >>> from xyzspaces.config.default import XYZConfig
    >>> config = XYZConfig.from_default()
    >>> api = TokenApi(config=config)
    >>> api.get_tokens()
    [...]
    """

    def __init__(
        self,
        config: Optional[XYZConfig] = None,
    ):
        """Instantiate a :class:`TokenApi` object.

        :param config:
        """
        xyzconfig = config
        if xyzconfig:
            super().__init__(xyzconfig)
        else:
            super().__init__(XYZConfig.from_default())

        self.headers = copy.deepcopy(self.xyzconfig.config["http_headers"])
        self.headers.pop("Content-Type")
        username = self.xyzconfig.config["credentials"]["HERE_USER"]
        password = self.xyzconfig.config["credentials"]["HERE_PASSWORD"]
        self.cookies.update(get_auth_cookies(username=username, password=password))

    # Public requests

    def get_token(self, token_id: str, **kwargs) -> dict:
        """Get info for given token ID.

        :param token_id: A string representing the requested token.
        :param kwargs: A dict with additional parameters passed to the HTTP
            request made when provided.
        :return: A JSON object with the information about the requested token.
        """
        path = f"/token-api/tokens/{token_id}.json"
        return self.get(path=path, **kwargs).json()

    # Protected requests, need to be called with access cookie.

    def get_tokens(self, **kwargs) -> list:
        """Get list of tokens for the authenticated user.

        :param kwargs: A dict with additional parameters passed to the HTTP
            request made when provided.
        :return: A list with information about all available tokens.
        """
        path = "/token-api/tokens"
        return self.get(path=path, **kwargs).json()

    def post_token(self, json: Dict = {}, **kwargs) -> dict:
        """Create a new permanent or temporary token.

        :param json: A dict with information about the token to be created.
        :param kwargs: A dict with additional parameters passed to the HTTP
            request made when provided.
        :return: A JSON object with all information about the created token.
        """
        path = "/token-api/tokens"
        return self.post(path=path, json=json, **kwargs).json()

    def delete_token(self, token_id: str, **kwargs) -> str:
        """Delete the token with the provided ID.

        :param token_id: A string representing a valid token.
        :param kwargs: A dict with additional parameters passed to the HTTP
            request made when provided.
        :return: An empty string if the operation was successful.
        """
        path = f"/token-api/tokens/{token_id}"
        return self.delete(path=path, **kwargs).text


class HubApi(Api):
    """XYZ RESTful Hub API abstraction.

    Instances of this API class allow to manage HERE XYZ spaces.

    API calls must be authenticated via a bearer token which needs to be
    provided as a ``credentials`` parameter when initialising an instance.

    A few convenience methods for calling HTTP methods directly are inherited
    from the :class:`Api` base class, and can also be used, although this class
    provides dedicated methods for the Hub API, like :meth:`HubApi.get_spaces()`
    starting with HTTP method names and an underscore, followed by a name
    resembling the respective API endpoint, in this case ``GET /hub/spaces``.

    Example:

    >>> from xyzspaces.apis import HubApi
    >>> from xyzspaces.config.default import XYZConfig
    >>> config = XYZConfig.from_default()
    >>> api = HubApi(config=config)
    >>> api.get_spaces()
    [...]

    This is based on the HERE XYZ Hub API specification defined here:
    https://xyz.api.here.com/hub/static/swagger/#/
    """

    def __init__(
        self,
        config: Optional[XYZConfig] = None,
    ):
        """Instantiate an :class:`HubApi` object.

        :param config: An object of `class:XYZConfig`, If not provied
            ``XYZ_TOKEN`` will be used from environment variable and
            other configurations will be used as defined in :py:mod:`default_config`
        """
        if config:
            super().__init__(config=config)
        else:
            super().__init__(config=XYZConfig.from_default())

    # Undocumented endpoints

    def get_hub(self, params: dict = None) -> dict:
        """Get basic information about the XYZ Hub.

        :param params: A dict holding the HTTP query parameters.
        :return: A JSON object with hub information.
        """
        if params is None:
            params = {"clientId": _CLIENT_ID}
        else:
            params.update({"clientId": _CLIENT_ID})
        return self.get(path="/hub", params=params).json()

    # Read Spaces

    def get_spaces(self, params: dict = None) -> dict:
        """Get Spaces information.

        :param params: A dict holding the HTTP query parameters.
        :return: A JSON object with list of spaces.
        """
        if params is None:
            params = {"clientId": _CLIENT_ID}
        else:
            params.update({"clientId": _CLIENT_ID})
        return self.get(path="/hub/spaces", params=params).json()

    def get_space(self, space_id: str, params: dict = None) -> dict:
        """Get a space by ID.

        :param space_id: The desired space ID.
        :param params: A dict for query params.
        :return: A JSON object with information about the space_id.
        """
        path = f"/hub/spaces/{space_id}"
        if params is None:
            params = {"clientId": _CLIENT_ID}
        else:
            params.update({"clientId": _CLIENT_ID})
        return self.get(path=path, params=params).json()

    # Edit Spaces

    def post_space(self, data: dict) -> dict:
        """Create a space.

        :param data: A dict describing the space to be created.
        :return: A JSON object with all information about the created space.
        """
        params = {"clientId": _CLIENT_ID}
        return self.post(path="/hub/spaces", json=data, params=params).json()

    def patch_space(self, space_id: str, data: dict) -> dict:
        """Update a space.

        :param space_id: A string representing the desired space ID.
        :param data: A JSON object describing the space attributes to be updated.
        :return: A JSON object with information about the updated space.
        """
        path = f"/hub/spaces/{space_id}"
        params = {"clientId": _CLIENT_ID}
        return self.patch(path=path, json=data, params=params).json()

    def delete_space(self, space_id: str) -> str:
        """Delete a space.

        :param space_id: A string representing desired space ID.
        :return: An empty string if the operation was successful.
        """
        path = f"/hub/spaces/{space_id}"
        params = {"clientId": _CLIENT_ID}
        return self.delete(path=path, params=params).text

    # Read Features

    def get_space_features(
        self,
        space_id: str,
        feature_ids: List[str],
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Get features by ID.

        :param space_id: The desired space ID.
        :param feature_ids: A list of feature_ids.
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A feature collection with all features inside the specified
            space.

        Example: Get single feature from space

        >>> feats = api.get_space_features(
        ...	    space_id=space_id, feature_ids=["GER", "BRA"])
        >>> print(feats)
        """
        path = f"/hub/spaces/{space_id}/features"
        params = {"id": feature_ids, "clientId": _CLIENT_ID}
        if force_2d:
            params["force2D"] = str(force_2d).lower()
        return self.get(path=path, params=params).json()

    def get_space_feature(
        self,
        space_id: str,
        feature_id: str,
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Get a feature by ID.

        :param space_id: The desired space ID.
        :param feature_id: The desired feature ID.
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A feature with the specified feature ID inside the space
            with the specified ID.

        Example: Read the feature from the space.

        >>>	feature = api.get_space_feature(
        ...     space_id=space_id, feature_id=feature_id)
        >>>	print(json.dumps(feature, indent=4, sort_keys=True))
        """
        path = f"/hub/spaces/{space_id}/features/{feature_id}"
        params = {"clientId": _CLIENT_ID}
        if force_2d:
            params["force2D"] = str(force_2d).lower()
        return self.get(path=path, params=params).json()

    def get_space_statistics(self, space_id: str) -> dict:
        """Get statistics.

        :param space_id: The desired space ID.
        :return: A JSON object with some statistics about the specified space.

        Example:

        >>>	stats = api.get_space_statistics(space_id=space_id)
        >>>	print(json.dumps(stats, indent=4, sort_keys=True))
        """
        path = f"/hub/spaces/{space_id}/statistics"
        params = {"clientId": _CLIENT_ID}
        return self.get(path=path, params=params).json()

    def get_space_bbox(
        self,
        space_id: str,
        bbox: List[Union[float, int]],
        tags: Optional[List[str]] = None,
        clip: Optional[bool] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        clustering: Optional[str] = None,
        clusteringParams: Optional[dict] = None,
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Get features inside some given bounding box.

        :param space_id: A string with the ID of the desired XYZ space.
        :param bbox: A list of four numbers representing the West, South,
            East and North margins, respectively, of the bounding box.
        :param tags: A list of strings holding tag values.
        :param clip: A Boolean indicating if the result should be clipped
            (default: False).
        :param limit: A max. number of features to return in the result.
        :param params: ...
        :param selection: ...
        :param skip_cache: ...
        :param clustering: ...
        :param clusteringParams: ...
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A dict representing a feature collection.

        Example:

        >>>	bb = [0, 0, 20, 20]
        >>>	bbox = api.get_space_bbox(space_id=space_id, bbox=bb)
        >>>	print(len(bbox["features"]))
        >>>	print(bbox["type"])
        """
        path = f"/hub/spaces/{space_id}/bbox"
        w, s, e, n = bbox
        q_params: Dict[str, str] = dict(
            west=str(w), south=str(s), east=str(e), north=str(n)
        )
        q_params.update({"clientId": _CLIENT_ID})
        if tags:
            q_params["tags"] = ",".join(tags)
        if clip:
            q_params["clip"] = str(clip).lower()
        if limit:
            q_params["limit"] = str(limit)
        if skip_cache:
            q_params["skipCache"] = str(skip_cache)  # pragma: no cover
        if clustering:
            q_params["clustering"] = clustering
        if params:
            q_params.update(params)
        if selection:
            q_params["selection"] = ",".join(selection)
        if clusteringParams:
            d = dict((f"clustering.{k}", v) for (k, v) in clusteringParams.items())
            q_params.update(d)
        if force_2d:
            q_params["force2D"] = str(force_2d).lower()
        return self.get(path=path, params=q_params).json()

    def get_space_tile(
        self,
        space_id: str,
        tile_type: str,
        tile_id: str,
        tags: Optional[List[str]] = None,
        clip: Optional[bool] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        clustering: Optional[str] = None,
        clusteringParams: Optional[dict] = None,
        margin: Optional[int] = None,
        limit: Optional[int] = None,
        force_2d: Optional[bool] = None,
        mode: Optional[str] = None,
        viz_sampling: Optional[str] = None,
    ) -> dict:
        """Get features in tile.

        :param space_id: A string with the ID of the desired XYZ space.
        :param tile_type: A string with the name of a tile type, one of
            "quadkeys", "web", "tms" or "here". See below.
        :param tile_id: A string holding a valid tile ID according to the
            specified ``tile_type``.
        :param tags: A list of strings holding tag values.
        :param clip: A Boolean indicating if the result should be clipped
            (default: False).
        :param margin: ...
        :param limit: A max. number of features to return in the result.
        :param params: ...
        :param selection: ...
        :param skip_cache: ...
        :param clustering: ...
        :param clusteringParams: ...
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :param mode: A string to indicate how to optimize the resultset and
            geometries for display. Allowed values are ``raw`` and ``viz``.
        :param viz_sampling: A string to indicate the sampling strength in
            case of ``mode=viz``. Allowed values are: ``low``, ``med``,
            ``high``, and ``off``, default: ``med``.
        :return: A dict representing a feature collection.

        Available tile types are:

        - quadkeys, `Virtual Earth Tile System
          <https://www.rigacci.org/wiki/doku.php/tecnica/gps_cartografia_gis/ve>`_,
        - web, `Tiled Web Map <https://en.wikipedia.org/wiki/Tiled_web_map>`_.
        - tms, `OSGEO Tile Map Service
          <https://wiki.osgeo.org/wiki/Tile_Map_Service_Specification>`_,
        - here, ?
        """
        path = f"/hub/spaces/{space_id}/tile/{tile_type}/{tile_id}"
        q_params: Dict[str, str] = {"clientId": _CLIENT_ID}
        if tags:
            q_params["tags"] = ",".join(tags)
        if clip:
            q_params["clip"] = str(clip).lower()
        if params:
            q_params.update(params)
        if selection:
            q_params["selection"] = ",".join(selection)
        if skip_cache:
            q_params["skipCache"] = str(skip_cache).lower()  # pragma: no cover
        if clustering:
            q_params["clustering"] = clustering
        if clusteringParams:
            d = dict((f"clustering.{k}", v) for (k, v) in clusteringParams.items())
            q_params.update(d)
        if margin:
            q_params["margin"] = str(margin)
        if limit:
            q_params["limit"] = str(limit)
        if force_2d:
            q_params["force2D"] = str(force_2d).lower()
        if mode:
            q_params["mode"] = str(mode).lower()
        if viz_sampling:
            q_params["vizSampling"] = str(viz_sampling).lower()
        return self.get(path=path, params=q_params).json()

    def get_space_search(
        self,
        space_id: str,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Search for features.

        :param space_id: A string with the ID of the desired XYZ space.
        :param tags: A list of strings holding tag values.
        :param limit: A max. number of features to return in the result.
        :param params: ...
        :param selection: ...
        :param skip_cache: ...
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A dict representing a feature collection.

        Example:

        >>>	feats = api.get_space_search(space_id=space_id)
        >>>	print(feats["type"] )
        >>>	print(len(feats["features"]) )
        """
        q_params: Dict[str, str] = {"clientId": _CLIENT_ID}
        if tags:
            q_params["tags"] = ",".join(tags)
        if limit:
            q_params["limit"] = str(limit)
        if params:
            q_params.update(params)
        if selection:
            q_params["selection"] = ",".join(selection)
        if skip_cache:
            q_params["skipCache"] = str(skip_cache).lower()  # pragma: no cover
        if force_2d:
            q_params["force2D"] = str(force_2d).lower()

        path = f"/hub/spaces/{space_id}/search"
        return self.get(path=path, params=q_params).json()

    # FIXME
    def get_space_iterate(
        self,
        space_id: str,
        limit: int,
        force_2d: Optional[bool] = None,
    ) -> Generator:
        """Iterate features in the space (yielding them one by one).

        :param space_id: A string representing desired space ID.
        :param limit: A max. number of features to return in the result.
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :yields: A feature in space.
        """
        path = f"/hub/spaces/{space_id}/iterate"
        params = {"limit": limit, "clientId": _CLIENT_ID}
        if force_2d:
            params["force2D"] = str(force_2d).lower()
        while True:
            res: dict = self.get(path=path, params=params).json()
            handle = res.get("handle", None)
            feats = res["features"]
            for feat in feats:
                yield feat
            if handle:
                params = {"limit": limit, "handle": handle}
            if handle is None or len(feats) < limit:
                break

    def get_space_all(self, space_id: str, limit: int, max_len=1000) -> dict:
        """Get all features as one single GeoJSON feature collection.

        This is a convenience method, not directly available in the XYZ API.
        It hides the API paging mechanism and returns all data in one chunk.
        So be careful if you don't know how much data you will get.

        :param space_id: A string representing desired space ID.
        :param limit: A max. number of features to return in the result.
        :param max_len: A max. number of features to return in the result.
        :return: A dict representing a feature collection.

        Example:

        >>>	fc = api.get_space_all(space_id=space_id, limit=100)
        >>>	print(len(fc["features"]) )
        >>>	print(fc["type"])
        """
        feature_it = self.get_space_iterate(space_id=space_id, limit=limit)
        gj = geojson.FeatureCollection(list(feature_it)[:max_len])
        return gj

    def get_space_count(self, space_id: str) -> dict:
        """Get feature count.

        :param space_id: A string with the ID of the desired XYZ space.
        :return: A dict containing the number of features inside the specified
            space.
        """
        path = f"/hub/spaces/{space_id}/count"
        params = {"clientId": _CLIENT_ID}
        return self.get(path=path, params=params).json()

    # Edit Features

    def put_space_features(
        self,
        space_id: str,
        data: dict,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> dict:
        """Create or replace multiple features.

        :param space_id: A string with the ID of the desired XYZ space.
        :param data: A JSON object describing one or more features to add.
        :param add_tags: A list of strings describing tags to be added to
            the features.
        :param remove_tags: A list of strings describing tags to be removed
            from the features.
        :return: A dict representing a feature collection.

        Example:

        >>> from xyzspaces.datasets import get_countries_data
        >>>	gj_countries = get_countries_data()
        >>>	features = api.put_space_features(
        ...     space_id=space_id,
        ...     data=gj_countries,
        ...     add_tags=["foo", "bar"],
        ...     remove_tags=["bar"],
        ... )
        >>> print(features)
        """
        path = f"/hub/spaces/{space_id}/features"
        params = join_string_lists(addTags=add_tags, removeTags=remove_tags)
        params.update({"clientId": _CLIENT_ID})
        return self.put(path=path, params=params, json=data, headers=self.headers).json()

    def post_space_features(
        self,
        space_id: str,
        data: dict,  # must be a feature collection
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> dict:
        """Modify multiple features in the space.

        :param space_id: A string with the ID of the desired XYZ space.
        :param data: A JSON object describing one or more features to
            modify.
        :param add_tags: A list of strings describing tags to be added to
            the features.
        :param remove_tags: A list of strings describing tags to be removed
            from the features.
        :return: A dict representing a feature collection.

        Example:

        >>> data = dict(type="FeatureCollection", features=[deu, ita])
        >>> space_features = api.post_space_features(
        ...     space_id=space_id, data=data)
        >>> print(space_features)
        """
        path = f"/hub/spaces/{space_id}/features"
        params = join_string_lists(addTags=add_tags, removeTags=remove_tags)
        params.update({"clientId": _CLIENT_ID})
        return self.post(path=path, params=params, json=data, headers=self.headers).json()

    def delete_space_features(
        self,
        space_id: str,
        id: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Delete multiple features from the space.

        :param space_id: A string with the ID of the desired XYZ space.
        :param id: A list of feature IDs to delete.
        :param tags: A list of strings describing tags the features to
            be deleted must have.
        :return: A response from API call.

        Example:

        >>>	deu = api.get_space_feature(space_id=space_id, feature_id="DEU")
        >>>	ita = api.get_space_feature(space_id=space_id, feature_id="ITA")
        >>>	deleted_features = api.delete_space_features(
        ...     space_id=space_id, id=["DEU", "ITA"])  # noqa: E501
        """
        path = f"/hub/spaces/{space_id}/features"
        params = {"clientId": _CLIENT_ID}
        if id:
            # TODO: The wildcard sign(*) could be used to delete all features
            #       in the space.
            params["id"] = ",".join(id)
        if tags:
            params["tags"] = ",".join(tags)
        return self.delete(path=path, params=params, headers=self.headers).text

    def put_space_feature(
        self,
        space_id: str,
        data: dict,
        feature_id: Optional[str] = None,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> dict:
        """Create or replace a single feature.

        :param space_id: A string with the ID of the desired XYZ space.
        :param data: A JSON object describing the feature to be added.
        :param feature_id: A string with the ID of the feature to be created.
        :param add_tags: A list of strings describing tags to be added to
            the feature.
        :param remove_tags: A list of strings describing tags to be removed
            from the feature.
        :return: A dict representing a feature.

        Example:

        >>>	api.put_space_feature(
        ...     space_id=space_id, feature_id=feature_id, data=fra)
        """
        if feature_id is not None:
            path = f"/hub/spaces/{space_id}/features/{feature_id}"
        else:
            path = f"/hub/spaces/{space_id}/features/"
        params = join_string_lists(addTags=add_tags, removeTags=remove_tags)
        params.update({"clientId": _CLIENT_ID})
        return self.put(path=path, params=params, json=data, headers=self.headers).json()

    def patch_space_feature(
        self,
        space_id: str,
        feature_id: str,
        data: dict,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> dict:
        """Patch a single feature in the space.

        :param space_id: A string with the ID of the desired XYZ space.
        :param feature_id: A string with the ID of the feature to be modified.
        :param data: A JSON object describing the feature to be changed.
        :param add_tags: A list of strings describing tags to be added to
            the feature.
        :param remove_tags: A list of strings describing tags to be removed
            from the feature.
        :return: A dict representing a feature.
        """
        path = f"/hub/spaces/{space_id}/features/{feature_id}"
        params = join_string_lists(addTags=add_tags, removeTags=remove_tags)
        params.update({"clientId": _CLIENT_ID})
        return self.patch(
            path=path, params=params, json=data, headers=self.headers
        ).json()

    def delete_space_feature(self, space_id: str, feature_id: str) -> str:
        """Delete a single feature from the space.

        :param space_id: A string with the ID of the desired XYZ space.
        :param feature_id: A string with the ID of the feature to be deleted.
        :return: An empty string if the operation was successful.
        """
        path = f"/hub/spaces/{space_id}/features/{feature_id}"
        params = {"clientId": _CLIENT_ID}
        return self.delete(path=path, params=params).text

    def get_space_spatial(
        self,
        space_id: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        ref_space_id: Optional[str] = None,
        ref_feature_id: Optional[str] = None,
        radius: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Get features with radius search.

        :param space_id: A string with the ID of the desired XYZ space.
        :param lat: A float in WGS'84 decimal degree (-90 to +90) of the center Point.
        :param lon: A float in WGS'84 decimal degree (-180 to +180) of the center Point.
        :param ref_space_id: A string as alternative for defining center coordinates,
            it is possible to reference a geometry in a space, hence it is needed to
            provide the ``ref_space_id`` where the referenced feature is stored.
            Always to use in combination with ``ref_feature_id``.
        :param ref_feature_id: A string as unique identifier of a feature in the
            referenced space.
            The geometry of that feature gets used for the spatial query.
            Always to use in combination with ``ref_space_id``.
        :param radius: An int in meter which defines the diameter of the search request.
        :param tags: A list of strings holding tag values.
        :param limit: A max. number of features to return in the result.
        :param params: A dict holding the HTTP query parameters.
        :param selection: A list of strings holding properties values.
        :param skip_cache: A Boolean if set to ``True`` the response is not returned from
            cache.
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A dict representing a feature collection.
        :raises ValueError: If incorrect params are passed, either ``lat`` and ``lon`` or
             ``ref_space_id`` and ``ref_feature_id`` must have a value.
        """
        if [lat, lon].count(None) and [ref_space_id, ref_feature_id].count(None):
            raise ValueError(
                "Incorrect params are passed: Either lat and lon "
                "or ref_space_id and ref_feature_id should have value."
            )
        path = f"/hub/spaces/{space_id}/spatial"
        q_params: Dict[str, str] = {"clientId": _CLIENT_ID}
        if lat:
            q_params["lat"] = str(lat)
        if lon:
            q_params["lon"] = str(lon)
        if ref_space_id:
            q_params["refSpaceId"] = ref_space_id
        if ref_feature_id:
            q_params["refFeatureId"] = ref_feature_id
        if radius:
            q_params["radius"] = str(radius)
        if tags:
            q_params["tags"] = ",".join(tags)
        if limit:
            q_params["limit"] = str(limit)
        if selection:
            q_params["selection"] = ",".join(selection)
        if skip_cache:
            q_params["skipCache"] = str(skip_cache).lower()  # pragma: no cover
        if params:
            q_params.update(params)
        if force_2d:
            q_params["force2D"] = str(force_2d).lower()
        return self.get(path=path, params=q_params).json()

    def post_space_spatial(
        self,
        space_id: str,
        data: dict,
        radius: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        force_2d: Optional[bool] = None,
    ) -> dict:
        """Post features which intersect the provided geometry.

        :param space_id: A string with the ID of the desired XYZ space.
        :param data: A JSON object which is getting used for the spatial search.
        :param radius: An int which defines the diameter(meters) of the search request.
        :param tags: A list of strings holding tag values.
        :param limit: A max. number of features to return in the result.
        :param params: A dict holding the HTTP query parameters.
        :param selection: A list of strings holding properties values.
        :param skip_cache: A Boolean if set to ``True`` the response is not returned from
            cache.
        :param force_2d: If set to True the features in the response
            will have only X and Y components, by default all
            x,y,z coordinates will be returned.
        :return: A dict representing a feature collection.
        """
        path = f"/hub/spaces/{space_id}/spatial"

        q_params: Dict[str, str] = {"clientId": _CLIENT_ID}
        if radius:
            q_params["radius"] = str(radius)
        if tags:
            q_params["tags"] = ",".join(tags)
        if limit:
            q_params["limit"] = str(limit)
        if selection:
            q_params["selection"] = ",".join(selection)
        if skip_cache:
            q_params["skipCache"] = str(skip_cache).lower()  # pragma: no cover
        if params:
            q_params.update(params)
        if force_2d:
            q_params["force2D"] = str(force_2d).lower()

        return self.post(
            path=path, params=q_params, json=data, headers=self.headers
        ).json()
