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
"""This module defines interactive map layer."""

import copy
import hashlib
import io
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import geopandas as gpd
from geojson import Feature, FeatureCollection
from geojson.geometry import Geometry
from geojson.mapping import GEO_INTERFACE_MARKER

from xyzspaces.iml.apis.data_interactive_api import DataInteractiveApi
from xyzspaces.iml.catalog import Catalog
from xyzspaces.utils import grouper

logger = logging.getLogger(__name__)


@dataclass
class HexbinClustering:
    """
    This class defines attributes for ``hexbin`` clustering algorithm.
    """

    clustering_type: str = "hexbin"
    absolute_resolution: Optional[int] = None
    resolution: Optional[int] = None
    relative_resolution: Optional[int] = None
    property: Optional[str] = None
    pointmode: Optional[bool] = None


@dataclass
class QuadbinClustering:
    """
    This class defines attributes for ``quadbin`` clustering algorithm.
    """

    clustering_type: str = "quadbin"
    no_buffer: bool = False
    relative_resolution: Optional[int] = None
    resolution: Optional[int] = None
    countmode: Optional[str] = None


class InteractiveMapApiResponse:
    """This class defines response returned from Interactive Map APIs."""

    def __init__(self, resp):
        self.response = resp

    def to_geojson(self) -> Union[Feature, FeatureCollection]:
        """Return response from API as :class:`geojson.Feature` or
        :class:`geojson.FeatureCollection`

        :return: Either GeoJSON Feature or FeatureCollection.
        :raises NotImplementedError: Response is incorrect.
        """
        if self.response["type"] == "Feature":
            return Feature(
                id=self.response["id"],
                geometry=self.response["geometry"],
                properties=self.response["properties"],
            )
        elif self.response["type"] == "FeatureCollection":
            return FeatureCollection(features=self.response["features"])
        else:
            raise NotImplementedError(
                "Response should be either Feature or FeatureCollection."
            )

    def to_geopandas(self) -> gpd.GeoDataFrame:
        """Return response from API as geopandas dataframe."""
        if self.response["type"] != "FeatureCollection":
            raise NotImplementedError("Response should be FeatureCollection.")
        fbytes = json.dumps(self.response).encode("utf-8")
        return gpd.read_file(io.BytesIO(fbytes))


class InteractiveMapLayer:
    """This class provides access to data stored in Interactive Map layers."""

    def __init__(self, layer_id: str, catalog: "Catalog"):
        """Initialize layer instance.

        :param layer_id: a string with the layer ID of this layer
        :param catalog: the instance of the Catalog this layer belongs to
        """
        self.id = layer_id
        self.catalog = catalog
        self._data_interactive_api: DataInteractiveApi = catalog._data_interactive_api

    def __repr__(self):
        """Return string representation of this instance."""
        return f"layer_id: {self.id}"

    @property
    def statistics(self) -> dict:
        """
        The statistical information of the layer.
        """
        stats: dict = self._data_interactive_api.get_statistics(
            layer_id=self.id, skip_cache=True
        )
        return stats

    def get_feature(
        self,
        feature_id: str,
        selection: Optional[List[str]] = None,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Return GeoJSON feature for the provided ``feature_id``.

        :param feature_id: Feature id which is to fetched.
        :param selection: A list, only these properties will be present in returned
            feature.
        :param force_2d: If set to ``True`` then features in the response will
            have only X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`Feature` object.
        """
        feature = self._data_interactive_api.get_feature(
            layer_id=self.id, feature_id=feature_id, selection=selection, force2d=force_2d
        )
        return InteractiveMapApiResponse(feature)

    def get_features(
        self,
        feature_ids: List[str],
        selection: Optional[List[str]] = None,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Return GeoJSON FeatureCollection for the provided feature_ids.

        :param feature_ids: A list of feature identifiers to fetch.
        :param selection: A list, only these properties will be present in returned
            features.
        :param force_2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`FeatureCollection` object.
        :raises ValueError: If ``feature_ids`` is empty list.
        """
        if not feature_ids:
            raise ValueError("Invalid input, please provide at least single feature_id")
        result = self._data_interactive_api.get_features(
            layer_id=self.id,
            feature_ids=feature_ids,
            selection=selection,
            force2d=force_2d,
        )
        return InteractiveMapApiResponse(result)

    def search_features(
        self,
        limit: int = 30000,
        params: Optional[Dict[str, Union[str, list, tuple]]] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Search for features in the layer based on the properties.

        :param limit: A maximum number of features to return in the result. Default is
            30000. Hard limit is 100000.
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
        :param force_2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`FeatureCollection` object.
        """  # noqa E501
        result = self._data_interactive_api.search_features(
            layer_id=self.id,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
            force2d=force_2d,
        )
        return InteractiveMapApiResponse(result)

    def iter_features(
        self,
        chunk_size: int = 30000,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force_2d: bool = False,
    ) -> Iterator[Feature]:
        """
        Return all the features in a Layer as Generator.

        :param chunk_size: A number of features to return in single iteration.
        :param selection: A list, only these properties will be present in returned
            features.
        :param skip_cache: If set to ``True`` the response is not returned from cache.
            Default is ``False``.
        :param force_2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :yields: A :class:`Feature` object.
        """
        page_token = None
        while True:
            resp = self._data_interactive_api.iter_features(
                layer_id=self.id,
                limit=chunk_size,
                page_token=page_token,
                selection=selection,
                skip_cache=skip_cache,
                force2d=force_2d,
            )
            page_token = resp.get("nextPageToken")
            features = resp["features"]
            for f in features:
                yield Feature(
                    id=f["id"], geometry=f["geometry"], properties=f["properties"]
                )
            if page_token is None:
                break

    def get_features_in_bounding_box(
        self,
        bounds: Tuple[float, float, float, float],
        clip: bool = False,
        limit: int = 30000,
        params: Optional[Dict[str, Union[str, list, tuple]]] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        clustering: Optional[Union[HexbinClustering, QuadbinClustering]] = None,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Return the features which are inside a bounding box stipulated by ``bounds``
        parameter.

        :param bounds: A tuple of four numbers representing the West, South,
            East and North margins, respectively, of the bounding box.
        :param clip: A Boolean indicating if the result should be clipped
            (default: False)
        :param limit: A maximum number of features to return in the result. Default is
            30000. Hard limit is 100000.
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
        :param clustering: An object of either :class:`HexbinClustering`
            or :class:`QuadbinClustering`.
        :param force_2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`FeatureCollection` object.
        """  # noqa E501
        clustering_params = {}
        if clustering:
            clustering_options = copy.deepcopy(vars(clustering))
            clustering_type = clustering_options.pop("clustering_type")
            for key, val in clustering_options.items():
                if val is not None:
                    init, *temp = key.split("_")
                    if temp:
                        new_key = "".join([init.lower(), *map(str.title, temp)])
                        clustering_params[new_key] = str(val).lower()
                    else:
                        clustering_params[init] = str(val).lower()
        else:
            clustering_type = None

        result = self._data_interactive_api.get_features_by_bbox(
            layer_id=self.id,
            bbox=bounds,
            clip=clip,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
            clustering=clustering_type,
            clustering_params=clustering_params if clustering_params else None,
            force2d=force_2d,
        )
        return InteractiveMapApiResponse(result)

    def spatial_search(
        self,
        lng: float,
        lat: float,
        radius: int,
        limit: int = 30000,
        params: Optional[Dict[str, Union[str, list, tuple]]] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Return the features which are inside the specified radius.

        :param lng: The longitude in WGS'84 decimal degree (-180 to +180) of the center
            Point.
        :param lat: The latitude in WGS'84 decimal degree (-90 to +90) of the center
            Point.
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
        :param force_2d: If set to ``True`` then features in the response will have only
            X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`FeatureCollection` object.
        """  # noqa E501
        result = self._data_interactive_api.get_features_with_radius_search(
            layer_id=self.id,
            lng=lng,
            lat=lat,
            radius=radius,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
            force2d=force_2d,
        )
        return InteractiveMapApiResponse(result)

    def spatial_search_geometry(
        self,
        geometry: Union[Feature, Geometry, dict, Any],
        radius: Optional[int] = None,
        limit: int = 30000,
        params: Optional[Dict[str, Union[str, list, tuple]]] = None,
        selection: Optional[List[str]] = None,
        skip_cache: bool = False,
        force_2d: bool = False,
    ) -> InteractiveMapApiResponse:
        """
        Return the features which are inside the specified radius and geometry.

        The origin point is calculated based on the provided geometry.

        :param geometry: Geometry which will be used in intersection.
        :type: a GeoJSON Feature of Geometry or any object that supports the
            ``__geo_interface__``.
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
        :param force_2d: If set to ``True`` then features in the response will have
            only X and Y components, else all x,y,z coordinates will be returned.
        :return: :class:`FeatureCollection` object.
        """  # noqa E501
        if hasattr(geometry, GEO_INTERFACE_MARKER):
            geometry = getattr(geometry, GEO_INTERFACE_MARKER)
        if hasattr(geometry, "geometry"):
            geometry = getattr(geometry, "geometry")
        result = self._data_interactive_api.get_features_with_geometry_intersection(
            layer_id=self.id,
            data=geometry,
            radius=radius,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
            force2d=force_2d,
        )
        return InteractiveMapApiResponse(result)

    def write_feature(self, feature_id: str, data: Union[Feature, dict]) -> None:
        """
        Write GeoJSON feature to Layer.

        :param feature_id: Identifier for the feature.
        :param data: GeoJSON feature which is written to layer.
        """

        self._data_interactive_api.put_feature(
            layer_id=self.id, feature_id=feature_id, data=data
        )

    def update_feature(self, feature_id: str, data: Union[Feature, dict]) -> None:
        """
        Update the GeoJSON feature in the Layer.

        :param feature_id: A feature_id to be updated.
        :param data: A GeoJSON Feature object to update.
        """
        self._data_interactive_api.patch_feature(
            layer_id=self.id, feature_id=feature_id, data=data
        )

    def delete_feature(self, feature_id: str) -> None:
        """
        Delete feature from the layer.

        :param feature_id: A feature_id to be deleted.
        """
        self._data_interactive_api.delete_feature(layer_id=self.id, feature_id=feature_id)

    def write_features(
        self,
        features: Optional[
            Union[FeatureCollection, dict, Iterator[Feature], List[Feature]]
        ] = None,
        from_file: Optional[Union[str, Path]] = None,
        feature_count: int = 2000,
    ) -> None:
        """
        Write GeoJSON FeatureCollection to layer.

        As API has a limitation on the size of features, features are divided into groups,
        and each group has number of features based on ``feature_count``.

        :param features: Features represented by :class:`FeatureCollection`, Dict,
            :class:`Iterator` or list of features.
        :param from_file: Path of GeoJSON file.
        :param feature_count: An int representing a number of features to upload at a
            time.
        """
        if features is not None:
            if isinstance(features, (FeatureCollection, dict)):
                feature_groups = grouper(
                    size=feature_count, iterable=features["features"]
                )
                self._upload_features(feature_groups=feature_groups)
            elif isinstance(features, (Iterator, list)):
                feature_groups = grouper(size=feature_count, iterable=features)
                self._upload_features(feature_groups=feature_groups)
        elif from_file is not None:
            with open(from_file) as fh:
                feature_col = json.load(fh)
            feature_groups = grouper(size=feature_count, iterable=feature_col["features"])
            self._upload_features(feature_groups=feature_groups)

    def _upload_features(self, feature_groups: Iterator[Union[Feature, Dict]]) -> None:
        features_set = set()
        for group in feature_groups:
            features_list = []
            for feature in group:
                if feature:
                    if "id" not in feature:
                        feature["id"] = hashlib.md5(
                            json.dumps(feature, sort_keys=True).encode("utf-8")
                        ).hexdigest()
                    if feature["id"] not in features_set:
                        features_set.add(feature["id"])
                        features_list.append(feature)
                    else:
                        logger.debug(
                            f"feature with id {feature['id']} is skipped due to "
                            f"duplicate id "
                        )
            feature_collection = FeatureCollection(features=features_list)
            self._data_interactive_api.put_features(
                layer_id=self.id, data=feature_collection
            )

    def update_features(self, data: Union[FeatureCollection, dict]) -> None:
        """
        Update multiple features provided as ``FeatureCollection`` object.

        :param data: A :class:`FeatureCollection` to be updated.
        """
        if data:
            self._data_interactive_api.post_features(layer_id=self.id, data=data)

    def delete_features(self, feature_ids: List[str]) -> None:
        """
        Delete features from layer.

        :param feature_ids: A list of feature_ids to be deleted.
        """
        if feature_ids:
            self._data_interactive_api.delete_features(
                layer_id=self.id, feature_ids=feature_ids
            )
