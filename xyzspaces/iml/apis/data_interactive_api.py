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
This module contains a :class:`DataInteractiveApiClient` class to perform API operations.

The HERE API reference documentation used in this module can be found here:
|interactive_api_reference|

.. |interactive_api_reference| raw:: html

   <a href="https://developer.here.com/documentation/data-api/api-reference-interactive.html" target="_blank">Interactive API Reference</a>
"""  # noqa E501
import copy
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from xyzspaces.iml.apis.api import Api
from xyzspaces.iml.auth import Auth


class DataInteractiveApi(Api):
    """
    This class provides access to HERE platform Data Interactive APIs.

    Interactive APIs offer a set of unique capabilities, enabling you to store, retrieve,
    search for, analyze and modify data at a feature (e.g., a place) and feature property
    (e.g., the name of the place) level. With interactive APIs, data is stored in GeoJSON
    and can be retrieved dynamically at any zoom level.
    """

    def __init__(
        self,
        base_url: str,
        auth: Auth,
        proxies: Optional[dict] = None,
    ):
        super().__init__(
            access_token=auth.token,
            proxies=proxies,
        )
        self.base_url = base_url

    @staticmethod
    def query_params_to_string(params: Dict[str, Union[str, list, tuple]]) -> str:
        """
        Convert query params in a dictionary to string.

        This method is required as character encoding needs to be skipped for ``,``
        to support ``OR`` condition, and if property value has any special character then
        character encoding is required. As python :mod:`requests` by default does
        encoding of all the characters hence, this needs to be handled separately.
        For more details please check: https://saeljira.it.here.com/browse/DH-1369.

        :param params: A dict to represent query params.
        :return: A string.
        """
        qlist = []
        for key, val in params.items():
            if isinstance(val, (list, tuple)):
                qval = ",".join((urllib.parse.quote_plus(str(v)) for v in val))
            else:
                qval = urllib.parse.quote_plus(str(val))
            qlist.append(f"{key}={qval}")
        params_str = "&".join(qlist)
        return params_str

    def get_feature(  # type: ignore[return]
        self,
        layer_id: str,
        feature_id: str,
        selection: Optional[List[str]] = None,
        force2d: bool = False,
    ) -> Dict:
        """
        Return the feature with the provided ``feature_id``.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_id: Feature id which is to fetched.
        :param selection: A list, only these properties will be present in  returned
            feature.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features/{feature_id}"
        params: Dict[str, Union[List, str]] = {"force2D": str(force2d).lower()}
        if selection:
            params["selection"] = [f"p.{name}" for name in selection]

        url = f"{self.base_url}{path}"
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            resp_dict: Dict = resp.json()
            return resp_dict
        else:
            self.raise_response_exception(resp)

    def get_features(  # type: ignore[return]
        self,
        layer_id: str,
        feature_ids: List,
        selection: Optional[List[str]] = None,
        force2d: bool = False,
    ) -> Dict:
        """
        Return all of the features found for the provided list of feature ids.

        The response is always a FeatureCollection, even if there are no features
        with the provided ids.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_ids: A list of feature_ids to fetch.
        :param selection: A list, only these properties will be present in  returned
            features.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features"
        params = {"id": feature_ids, "force2D": str(force2d).lower()}
        if selection:
            params["selection"] = [f"p.{name}" for name in selection]
        url = f"{self.base_url}{path}"
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_statistics(  # type: ignore[return]  # noqa E501
        self, layer_id: str, skip_cache: bool = False
    ) -> Dict:
        """
        Return statistical information about this layer.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/statistics"
        params = {"skipCache": str(skip_cache).lower()}
        url = f"{self.base_url}{path}"
        resp = self.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_features_by_bbox(  # type: ignore[return]
        self,
        layer_id: str,
        bbox: tuple,
        clip: bool = False,
        limit: int = 30000,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        clustering: Optional[str] = None,
        clustering_params: Optional[Dict] = None,
        force2d: bool = False,
    ) -> Dict:
        """
        Return the features which are inside a bounding box stipulated by ``bbox``
        parameter.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param bbox: A list of four numbers representing the West, South,
            East and North margins, respectively, of the bounding box.
        :param clip: A Boolean indicating if the result should be clipped
            (default: False).
        :param limit: A maximum number of features to return in the result. Default
            is 30000. Hard limit is 100000.
        :param params: A dict to represent additional filters on features to be searched.

            Examples:

            * ``params={"name": "foo"}`` returns all features with a value of property ``name`` equal to ``foo``.

            * ``params={"name!": "foo"}`` returns all features with a value of property ``name`` not equal to ``foo``.

            * ``params={"count=gte": "10"}`` returns all features with a value of property ``count`` greater than or equal to ``10``.

            * ``params={"count=lte": "10"}`` returns all features with a value of property ``count`` less than or equal to ``10``.

            * ``params={"count=gt": "10"}`` returns all features with a value of property ``count`` greater than ``10``.

            * ``params={"count=lt": "10"}`` returns all features with a value of property ``count`` less than ``10``.

            * ``params={"name=cs": "bar"}`` returns all features with a value of property ``name`` which contains``bar``.

        :param selection: A list, only these properties will be present in  returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param clustering: The clustering algorithm to apply to the data within the
            result. Clustering algorithms supported: ``hexbin``, ``quadbin``.
        :param clustering_params: Parameters for the chosen clustering algorithm.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """  # noqa E501
        path = f"/layers/{layer_id}/bbox"
        url = f"{self.base_url}{path}"
        if params:
            params_str = self.query_params_to_string(params)
            url = "?".join((url, params_str))

        bbox_str = ",".join([str(i) for i in bbox])
        q_params = {
            "bbox": bbox_str,
            "force2D": str(force2d).lower(),
            "clip": str(clip).lower(),
            "limit": limit,
            "skipCache": str(skip_cache).lower(),
        }
        if selection:
            q_params["selection"] = [f"p.{name}" for name in selection]
        if clustering is not None:
            q_params["clustering"] = clustering
        if clustering_params:
            d = dict((f"clustering.{k}", v) for (k, v) in clustering_params.items())
            q_params.update(d)

        resp = self.get(url, params=q_params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_features_in_tile(  # type: ignore[return]
        self,
        layer_id: str,
        tile_type: str,
        tile_id: str,
        clip: bool = False,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        clustering: Optional[str] = None,
        clustering_params: Optional[Dict] = None,
        margin: Optional[int] = 0,
        limit: int = 30000,
        force2d: bool = False,
    ) -> Dict:
        """
        Retrieve features in tile.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param tile_type: A string with the name of a tile type, one of
            "quadkeys", "web", "tms" or "here". The type of tile identifier.
            "quadkey" - Virtual Earth, "web" - Web Mercator,
            "tms" - OSGEO Tile Map Service, "here" - Here Tile Schema.
        :param tile_id: The tile identifier can be provided as quadkey (1),
            Web Mercator level,x,y coordinates (1_1_0) or
            OSGEO Tile Map Service level,x,y (1_1_0).
        :param clip: A Boolean indicating if the result should be clipped
            (default: False).
        :param params: A dict to represent additional filters on features to be searched.

            Examples:

            * ``params={"name": "foo"}`` returns all features with a value of property ``name`` equal to ``foo``.

            * ``params={"name!": "foo"}`` returns all features with a value of property ``name`` not equal to ``foo``.

            * ``params={"count=gte": "10"}`` returns all features with a value of property ``count`` greater than or equal to ``10``.

            * ``params={"count=lte": "10"}`` returns all features with a value of property ``count`` less than or equal to ``10``.

            * ``params={"count=gt": "10"}`` returns all features with a value of property ``count`` greater than ``10``.

            * ``params={"count=lt": "10"}`` returns all features with a value of property ``count`` less than ``10``.

            * ``params={"name=cs": "bar"}`` returns all features with a value of property ``name`` which contains``bar``.

        :param selection: A list, only these properties will be present in  returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param clustering: The clustering algorithm to apply to the data within the
            result. Clustering algorithms supported: ``hexbin``, ``quadbin``.
        :param clustering_params: Parameters for the chosen clustering algorithm.
        :param margin: Margin in pixels on the respective projected level around the tile.
            Default is 0.
        :param limit: The maximum number of features in the response. Default is 30000.
            Hard limit is 100000.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """  # noqa E501
        path = f"/layers/{layer_id}/tile/{tile_type}/{tile_id}"
        url = f"{self.base_url}{path}"
        if params:
            params_str = self.query_params_to_string(params)
            url = "?".join((url, params_str))
        q_params = {
            "force2D": str(force2d).lower(),
            "clip": str(clip).lower(),
            "limit": limit,
            "skipCache": str(skip_cache).lower(),
            "margin": margin,
        }
        if selection:
            q_params["selection"] = [f"p.{name}" for name in selection]
        if clustering is not None:
            q_params["clustering"] = clustering
        if clustering_params:
            d = dict((f"clustering.{k}", v) for (k, v) in clustering_params.items())
            q_params.update(d)
        resp = self.get(url, params=q_params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_features_with_radius_search(  # type: ignore[return]
        self,
        layer_id: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        ref_catalog: Optional[str] = None,
        ref_layer_id: Optional[str] = None,
        ref_feature_id: Optional[str] = None,
        radius: Optional[int] = None,
        limit: int = 30000,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force2d: bool = False,
    ) -> Dict:
        """
        Retrieve the features which are inside the specified radius.

        The origin radius point is calculated based either on latitude & longitude
        or by specifying a feature's geometry.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param lat: The latitude in WGS'84 decimal degree (-90 to +90) of the center
            Point.
        :param lng: The longitude in WGS'84 decimal degree (-180 to +180) of the center
            Point.
        :param ref_catalog: The catalog HRN where the layer containing the referenced
            feature is stored. Always to use in combination with ``ref_feature_id``.
        :param ref_layer_id: As alternative for defining center coordinates, it is
            possible to reference a geometry in a layer. Therefore it is needed to
            provide the layer id where the referenced feature is stored.
            Always to use in combination with ``ref_feature_id``.
        :param ref_feature_id: The unique identifier of a feature in the referenced layer.
            The geometry of that feature gets used for the spatial query.
            Always to use in combination with ``ref_catalog`` and ``ref_layer_id``.
        :param radius: Radius in meter which defines the diameter of the search request.
        :param limit: The maximum number of features in the response. Default is 30000.
            Hard limit is 100000.
        :param params: A dict to represent additional filters on features to be searched.

            Examples:

            * ``params={"name": "foo"}`` returns all features with a value of property ``name`` equal to ``foo``.

            * ``params={"name!": "foo"}`` returns all features with a value of property ``name`` not equal to ``foo``.

            * ``params={"count=gte": "10"}`` returns all features with a value of property ``count`` greater than or equal to ``10``.

            * ``params={"count=lte": "10"}`` returns all features with a value of property ``count`` less than or equal to ``10``.

            * ``params={"count=gt": "10"}`` returns all features with a value of property ``count`` greater than ``10``.

            * ``params={"count=lt": "10"}`` returns all features with a value of property ``count`` less than ``10``.

            * ``params={"name=cs": "bar"}`` returns all features with a value of property ``name`` which contains``bar``.

        :param selection: A list, only these properties will be present in returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """  # noqa E501
        path = f"/layers/{layer_id}/spatial"
        url = f"{self.base_url}{path}"
        if params:
            params_str = self.query_params_to_string(params)
            url = "?".join((url, params_str))
        q_params: Dict[str, Any] = {
            "force2D": str(force2d).lower(),
            "limit": limit,
            "skipCache": str(skip_cache).lower(),
        }
        if lat is not None:
            q_params["lat"] = str(lat)
        if lng is not None:
            q_params["lon"] = str(lng)
        if ref_catalog is not None:
            q_params["refCatalogHrn"] = ref_catalog
        if ref_layer_id is not None:
            q_params["refLayerId"] = ref_catalog
        if ref_feature_id is not None:
            q_params["refFeatureId"] = ref_feature_id
        if radius is not None:
            q_params["radius"] = str(radius)
        if selection:
            q_params["selection"] = [f"p.{name}" for name in selection]
        resp = self.get(url, params=q_params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def get_features_with_geometry_intersection(  # type: ignore[return]
        self,
        layer_id: str,
        data: dict,
        radius: Optional[int] = None,
        limit: int = 30000,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force2d: bool = False,
    ) -> Dict:
        """
        Retrieve the features which are inside the specified radius and geometry.

        The origin point is calculated based on the geometry provided as payload.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param data: Geometry which will be used in intersection.
        :param radius: Radius in meter which defines the diameter of the search request.
        :param limit: The maximum number of features in the response. Default is 30000.
            Hard limit is 100000.
        :param params: A dict to represent additional filters on features to be searched.

            Examples:

            * ``params={"name": "foo"}`` returns all features with a value of property ``name`` equal to ``foo``.

            * ``params={"name!": "foo"}`` returns all features with a value of property ``name`` not equal to ``foo``.

            * ``params={"count=gte": "10"}`` returns all features with a value of property ``count`` greater than or equal to ``10``.

            * ``params={"count=lte": "10"}`` returns all features with a value of property ``count`` less than or equal to ``10``.

            * ``params={"count=gt": "10"}`` returns all features with a value of property ``count`` greater than ``10``.

            * ``params={"count=lt": "10"}`` returns all features with a value of property ``count`` less than ``10``.

            * ``params={"name=cs": "bar"}`` returns all features with a value of property ``name`` which contains``bar``.

        :param selection: A list, only these properties will be present in returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """  # noqa E501
        path = f"/layers/{layer_id}/spatial"
        url = f"{self.base_url}{path}"
        if params:
            params_str = self.query_params_to_string(params)
            url = "?".join((url, params_str))
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/geo+json"
        q_params: Dict[str, Any] = {
            "force2D": str(force2d).lower(),
            "limit": limit,
            "skipCache": str(skip_cache).lower(),
        }

        if radius is not None:
            q_params["radius"] = str(radius)
        if selection:
            q_params["selection"] = [f"p.{name}" for name in selection]
        resp = self.post(url=url, params=q_params, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def search_features(  # type: ignore[return]
        self,
        layer_id: str,
        limit: int = 30000,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force2d: bool = False,
    ) -> Dict:
        """
        Search for features in the layer.

        The results are unordered and the request does not allow to continue the search,

        :param layer_id: Identifier of the Interactive Map Layer.
        :param limit: The maximum number of features in the response. Default is 30000.
            Hard limit is 100000.
        :param params: A dict to represent additional filters on features to be searched.

            Examples:

            * ``params={"name": "foo"}`` returns all features with a value of property ``name`` equal to ``foo``.

            * ``params={"name!": "foo"}`` returns all features with a value of property ``name`` not equal to ``foo``.

            * ``params={"count=gte": "10"}`` returns all features with a value of property ``count`` greater than or equal to ``10``.

            * ``params={"count=lte": "10"}`` returns all features with a value of property ``count`` less than or equal to ``10``.

            * ``params={"count=gt": "10"}`` returns all features with a value of property ``count`` greater than ``10``.

            * ``params={"count=lt": "10"}`` returns all features with a value of property ``count`` less than ``10``.

            * ``params={"name=cs": "bar"}`` returns all features with a value of property ``name`` which contains``bar``.

        :param selection: A list, only these properties will be present in returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """  # noqa E501
        path = f"/layers/{layer_id}/search"
        url = f"{self.base_url}{path}"
        if params:
            params_str = self.query_params_to_string(params)
            url = "?".join((url, params_str))
        q_params: Dict[str, Any] = {
            "force2D": str(force2d).lower(),
            "limit": limit,
            "skipCache": str(skip_cache).lower(),
        }

        if selection:
            q_params["selection"] = [f"p.{name}" for name in selection]
        resp = self.get(url, params=q_params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def iter_features(  # type: ignore[return]
        self,
        layer_id: str,
        limit: int = 30000,
        page_token: Optional[str] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force2d: bool = False,
    ) -> Dict:
        """
        Iterate over all of the features in the layer.

        The features in the response are ordered  so that no feature is returned twice.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param limit: The maximum number of features in the response in single iteration.
            Default is 30000. Hard limit is 100000.
        :param page_token: The page token where the iteration will continue.
        :param selection: A list, only these properties will be present in returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param force2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/iterate"
        url = f"{self.base_url}{path}"
        params: Dict[str, Any] = {
            "limit": limit,
            "force2D": str(force2d).lower(),
            "skipCache": str(skip_cache).lower(),
        }
        if selection:
            params["selection"] = [f"p.{name}" for name in selection]
        if page_token:
            params["pageToken"] = page_token
        resp = self.get(url=url, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def put_features(self, layer_id: str, data: dict):
        """
        Create or replace the provided features.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param data: Request body representing FeatureCollection to create or replace.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features"
        url = f"{self.base_url}{path}"
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/geo+json"
        resp = self.put(url=url, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def post_features(self, layer_id: str, data: dict):
        """
        Create or patch features.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param data: Request body representing FeatureCollection to create or update.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features"
        url = f"{self.base_url}{path}"
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/geo+json"
        resp = self.post(url=url, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def delete_features(self, layer_id: str, feature_ids: List[str]):
        """
        Delete multiple features from the layer.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_ids: A list of feature_ids to be deleted.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features"
        url = f"{self.base_url}{path}"
        params = {"id": feature_ids}
        resp = self.delete(url=url, params=params)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 204:
            return resp.text
        else:
            self.raise_response_exception(resp)

    def put_feature(self, layer_id: str, feature_id: str, data: dict):
        """
        Creates or replace a feature in the layer.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_id: Feature id which is to fetched.
        :param data: Request body representing feature to create or replace.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features/{feature_id}"
        url = f"{self.base_url}{path}"
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/geo+json"
        resp = self.put(url=url, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def patch_feature(self, layer_id: str, feature_id: str, data: dict):
        """
        Patch an existing feature.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_id: Feature id which is to fetched.
        :param data: Request body representing feature to change.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features/{feature_id}"
        url = f"{self.base_url}{path}"
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/geo+json"
        resp = self.patch(url=url, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            self.raise_response_exception(resp)

    def delete_feature(self, layer_id: str, feature_id: str):
        """
        Delete an existing feature.

        :param layer_id: Identifier of the Interactive Map Layer.
        :param feature_id: Feature id which is to fetched.
        :return: Response from the API.
        """
        path = f"/layers/{layer_id}/features/{feature_id}"
        url = f"{self.base_url}{path}"
        resp = self.delete(url=url)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 204:
            return resp.text
        else:
            self.raise_response_exception(resp)
