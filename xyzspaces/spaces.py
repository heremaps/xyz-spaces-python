# Copyright (C) 2019-2020 HERE Europe B.V.
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
An more Pythonic abstraction for XYZ Spaces.

This contains only one class for an XYZ "space" which in turn provides access
to "features". There is no separate class abstraction for single features,
but they are taken to be valid :class:`geojson.GeoJSON` objects. Various
other bits of the XYZ Hub API are simply returned as-is, usually wrapped in
dictionaries, like the "statistics" of some given XYZ space.
"""

import concurrent.futures
import csv
import json
import logging
import tempfile
from functools import partial
from multiprocessing import Manager
from typing import Any, Dict, Generator, List, Optional, Union

import fiona
import geopandas as gpd
from geojson import Feature, GeoJSON

from .apis import HubApi
from .utils import divide_bbox, grouper, wkt_to_geojson

logger = logging.getLogger(__name__)


class Space:
    """
    An abstraction for XYZ Spaces.

    A space object is created with an existing, authenticated XYZ Hub API
    instance.

    Example:

    >>> space = Space.new(...)
    >>> space.delete()
    >>> for feat in space.iter_feature():
    ....   print(feat["id"])
    """

    @classmethod
    def from_id(cls, space_id: str) -> "Space":
        """Instantiate a space object for an existing space ID."""
        api = HubApi()
        obj = cls(api)
        obj._info = api.get_space(space_id=space_id)
        return obj

    @classmethod
    def new(
        cls,
        title: str,
        description: str,
        space_id: Optional[str] = None,
        schema: str = None,
        enable_uuid: Optional[bool] = None,
        listeners: Optional[Dict[str, Union[str, int]]] = None,
        shared: Optional[bool] = None,
    ) -> "Space":
        """Create new space object with given title and description.

        Optionally, the desired space ID can be provided as well, and will
        be used if still available.

        :param title: A string representing the title of the space.
        :param description: A string representing a description of the space.
        :param space_id: A string representing space_id.
        :param schema: JSON object or URL to be added as a schema for space.
        :param enable_uuid: A boolean if set ``True`` it will create
            additional activity log space to log the activities in current space.
        :param listeners: A dict for activity log listener params.
        :param shared: A boolean, if set to ``True``, space will be shared with
            other users having XYZ account, they will be able to read from the
            space using their own token. By default space will not be a shared space.
        :return: A object of :class:`Space`.
        """
        api = HubApi()
        obj = cls(api)
        data: Dict[Any, Any] = {"title": title, "description": description}

        if schema is not None:
            data.setdefault("processors", []).append(
                {"id": "schema-validator", "params": dict(schema=schema)}
            )
        if enable_uuid is not None and listeners is not None:
            data["enableUUID"] = "true"
            data.setdefault("listeners", []).append(listeners)
        if space_id is not None:
            data["id"] = space_id
        if shared is True:
            data["shared"] = "true"
        obj._info = api.post_space(data=data)
        return obj

    @classmethod
    def virtual(
        cls, title: str, description: str, **kwargs: Dict[str, Dict]
    ) -> "Space":
        """Create a new virtual-space.

        Virtual-space references one or multiple spaces. A virtual-space is
        described by definition which references other existing spaces
        (the upstream spaces). Queries being done to a virtual-space will
        return the features of its upstream spaces combined. There are
        different predefined operations of how to combine the features of the
        upstream spaces. In order to use virtual spaces feature user needs to
        have HERE Data Hub paid plan.
        Plans can be found here: `HERE Data Hub <https://developer.here.com/pricing>`_.

        :param title: A string representing the title of the virtual-space.
        :param description: A string representing a description of the virtual-space.
        :param kwargs: A dict for the operation to perform on upstream spaces.
        :return: An object of :class:`Space`.
        """
        api = HubApi()
        obj = cls(api)
        data: Dict[str, Any] = {"title": title, "description": description}
        storage: Dict[str, Any] = dict(id="virtualspace")
        storage["params"] = kwargs
        data["storage"] = storage
        obj._info = api.post_space(data=data)
        return obj

    def __init__(self, api: Optional[HubApi] = None):
        """Instantiate a space object, optionally with authenticated api instance."""
        self.api = api or HubApi()
        self._info: dict = {}

    def __repr__(self):
        """Return string representation of this instance."""
        return f"space_id: {self._info.get('id', '')}"

    @property
    def info(self):
        """Space config information."""
        if "id" in self._info:
            return self.api.get_space(self._info["id"])
        return {}

    def list(self, owner: str = "me", include_rights: bool = False) -> Dict:
        """Return list of spaces for given owner with access rights if desired.

        This does not modify the space object itself.

        :param owner: A string representing the owner.
        :param include_rights: A boolean. If set to True, the access rights for each
            space are included in the response.
        :return: A JSON object with list of spaces.
        """
        data: Dict[str, Any] = {
            "owner": owner,
            "include_rights": include_rights,
        }
        return self.api.get_spaces(params=data)

    def read(self, id: str) -> "Space":
        """Read existing space object for given space ID."""
        self._info = self.api.get_space(space_id=id)
        return self

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tagging_rules: Optional[Dict[str, str]] = None,
        schema: str = None,
        shared: Optional[bool] = None,
    ) -> Dict:
        """Update space attributes.

        This method updates title, description, schema, shared status or tagging
        rules of space, at least one of these params should have a non-default
        value to update the space.

        Does update the space in the XYZ storage and this object mirroring it.
        Also apply the tags based on rules mentioned in `tagging_rules` dict.

        :param title: A string representing the title of the space.
        :param description: A string representing a description of the space.
        :param tagging_rules: A dict where the key is the tag to be applied to
            all features matching the JSON-path expression being the value.
        :param schema: JSON object or URL to be added as schema for space.
        :param shared: A boolean, if set to ``True``, space will be shared with
            other users having XYZ account, they will be able to read from the
            space using their own token. If set to ``False`` space will be unshared.
        :return: A response from API.

        Example:

        >>> from xyzspaces import XYZ
        >>> xyz = XYZ(credentials="XYZ_TOKEN")
        >>> space = xyz.spaces.new(title="new space", description="new space")
        >>> tagging_rules = {"large": "$.features[?(@.properties.area>=500)]"}
        >>> space.update(title="updated title",
        ...              description="updated description",
        ...              tagging_rules=tagging_rules)
        """
        space_id = self._info["id"]
        data: Dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if tagging_rules is not None:
            data.setdefault("processors", []).append(
                {
                    "id": "rule-tagger",
                    "params": dict(taggingRules=tagging_rules),
                }
            )
        if schema:
            data.setdefault("processors", []).append(
                {"id": "schema-validator", "params": dict(schema=schema)}
            )
        if shared is True:
            data["shared"] = "true"
        elif shared is False:
            data["shared"] = "false"

        return self.api.patch_space(space_id=space_id, data=data)

    def delete(self):
        """Delete this space object."""
        if self._info:
            self.api.delete_space(space_id=self._info["id"])
        self._info = {}

    def get_statistics(self) -> dict:
        """
        Get statistics for this space object.

        :return: A JSON object with some statistics about the specified space.
        """
        return self.api.get_space_statistics(space_id=self._info["id"])

    def search(
        self,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
    ) -> Generator[Feature, None, None]:
        """
        Search features for this space object.

        :param tags: A list of strings holding tag values.
        :param limit: A max. number of features to return in the result.
        :param params: ...
        :param selection: ...
        :param skip_cache: ...
        :yields: A Feature object.
        """
        features = self.api.get_space_search(
            space_id=self._info["id"],
            tags=tags,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
        )
        for f in features["features"]:
            yield f

    def iter_feature(self) -> Generator[Feature, None, None]:
        """
        Iterate over features in this space object.

        :yields: A Feature object.
        """
        for feature in self.api.get_space_iterate(
            space_id=self._info["id"], limit=100
        ):
            yield feature

    def get_feature(self, feature_id: str) -> GeoJSON:
        """
        Retrieve one GeoJSON feature with given ID from this space.

        :param feature_id: Feature id which is to fetched.
        :return: A GeoJSON representing a feature with the specified feature
             ID inside the space.
        """
        res = self.api.get_space_feature(
            space_id=self._info["id"], feature_id=feature_id
        )
        return GeoJSON(res)

    def add_feature(
        self,
        data: GeoJSON,
        feature_id: Optional[str] = None,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> GeoJSON:
        """
        Add one GeoJSON feature with given ID in this space.

        :param data: A JSON object describing the feature to be added.
        :param feature_id: A string with the ID of the feature to be created.
        :param add_tags: A list of strings describing tags to be added to
            the feature.
        :param remove_tags: A list of strings describing tags to be removed
            from the feature.
        :return: A GeoJSON representing a feature.
        """
        res = self.api.put_space_feature(
            space_id=self._info["id"],
            feature_id=feature_id,
            data=data,
            add_tags=add_tags,
            remove_tags=remove_tags,
        )
        return GeoJSON(res)

    def update_feature(
        self,
        feature_id: str,
        data: dict,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> GeoJSON:
        """
        Update one GeoJSON feature with given ID in this space.

        :param feature_id: A string with the ID of the feature to be modified.
        :param data: A JSON object describing the feature to be changed.
        :param add_tags: A list of strings describing tags to be added to
            the feature.
        :param remove_tags: A list of strings describing tags to be removed
            from the feature.
        :return: A GeoJSON representing a feature.
        """
        res = self.api.patch_space_feature(
            space_id=self._info["id"],
            feature_id=feature_id,
            data=data,
            add_tags=add_tags,
            remove_tags=remove_tags,
        )
        return GeoJSON(res)

    def delete_feature(self, feature_id: str):
        """
        Delete one GeoJSON feature with given ID in this space.

        :param feature_id: A string with the ID of the feature to be deleted.
        :return: An empty string if the operation was successful.
        """
        return self.api.delete_space_feature(
            space_id=self._info["id"], feature_id=feature_id
        )

    def get_features(self, feature_ids: List[str]) -> GeoJSON:
        """
        Retrieve one GeoJSON feature with given ID from this space.

        :param feature_ids: A list of feature_ids.
        :return: A feature collection with all features inside the specified
            space.
        """
        res = self.api.get_space_features(
            space_id=self._info["id"], feature_ids=feature_ids
        )
        return GeoJSON(res)

    def add_features(
        self,
        features: GeoJSON,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
        features_size: int = 2000,
        chunk_size: int = 1,
    ) -> GeoJSON:
        """
        Add GeoJSON features to this space.

        As API has a limitation on the size of features, features are divided into chunks,
        and multiple processes will process those chunks.
        Each chunk has a number of features based on the value of ``features_size``.
        Each process handles chunks based on the value of ``chunk_size``.

        :param features: A JSON object describing one or more features to add.
        :param add_tags: A list of strings describing tags to be added to
            the features.
        :param remove_tags: A list of strings describing tags to be removed
            from the features.
        :param features_size: An int representing a number of features to upload at a
            time.
        :param chunk_size: Number of chunks each process to handle. The default value is
            1, for a large number of features please use `chunk_size` greater than 1
            to get better results in terms of performance.
        :return: A GeoJSON representing a feature collection.
        """
        space_id = self._info["id"]
        total = 0
        if len(features["features"]) > features_size:
            groups = grouper(features_size, features["features"])
            part_func = partial(
                self._upload_features,
                add_tags=add_tags,
                remove_tags=remove_tags,
            )
            with concurrent.futures.ProcessPoolExecutor() as executor:
                for ft in executor.map(
                    part_func, groups, chunksize=chunk_size
                ):
                    logger.info(f"features processed: {ft}")
                    total += ft
            logger.info(f"{total} features are uploaded on space: {space_id}")
        else:
            res = self.api.put_space_features(
                space_id=space_id,
                data=features,
                add_tags=add_tags,
                remove_tags=remove_tags,
            )
            return GeoJSON(res)

    def _upload_features(
        self,
        features,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ):
        features = [f for f in features if f]
        feature_collection = dict(type="FeatureCollection", features=features)
        self.api.put_space_features(
            space_id=self._info["id"],
            data=feature_collection,
            add_tags=add_tags,
            remove_tags=remove_tags,
        )
        return len(features)

    def update_features(
        self,
        features: GeoJSON,  # must be a feature collection
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None,
    ) -> GeoJSON:
        """
        Update GeoJSON features in this space.

        :param features: A JSON object describing one or more features to
            modify.
        :param add_tags: A list of strings describing tags to be added to
            the features.
        :param remove_tags: A list of strings describing tags to be removed
            from the features.
        :return: A GeoJSON representing a feature collection.
        """
        space_id = self._info["id"]
        res = self.api.post_space_features(
            space_id=space_id,
            data=features,
            add_tags=add_tags,
            remove_tags=remove_tags,
        )
        return GeoJSON(res)

    def delete_features(
        self, feature_ids: List[str], tags: Optional[List[str]] = None
    ):
        """
        Delete GeoJSON features in this space.

        :param feature_ids: A list of feature IDs to delete.
        :param tags: A list of strings describing tags the features to
            be deleted must have.
        :return: A response from API.
        """
        space_id = self._info["id"]
        return self.api.delete_space_features(
            space_id=space_id, id=feature_ids, tags=tags
        )

    def features_in_bbox(
        self,
        bbox: List[Union[float, int]],
        tags: Optional[List[str]] = None,
        clip: Optional[bool] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        clustering: Optional[str] = None,
        clustering_params: Optional[dict] = None,
    ) -> Generator[Feature, None, None]:
        """
        Get features inside some given bounding box.

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
        :param clustering_params: ...
        :yields: A Feature object.
        """
        features = self.api.get_space_bbox(
            space_id=self._info["id"],
            bbox=bbox,
            tags=tags,
            clip=clip,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
            clustering=clustering,
            clusteringParams=clustering_params,
        )
        for f in features["features"]:
            yield f

    def features_in_tile(
        self,
        tile_type: str,
        tile_id: str,
        tags: Optional[List[str]] = None,
        clip: Optional[bool] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        clustering: Optional[str] = None,
        clustering_params: Optional[dict] = None,
        margin: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Generator[Feature, None, None]:
        """
        Get features in tile.

        :param tile_type: A string with the name of a tile type, one of
            "quadkeys", "web", "tms" or "here". See below.
        :param tile_id: A string holding a valid tile ID according to the
            specified ``tile_type``.
        :param tags: A list of strings holding tag values.
        :param clip: A Boolean indicating if the result should be clipped
            (default: False).
        :param params: ...
        :param selection: ...
        :param skip_cache: ...
        :param clustering: ...
        :param clustering_params: ...
        :param margin: ...
        :param limit: A max. number of features to return in the result.
        :yields: A Feature object.
        :raises ValueError: If `tile_type` is invalid, valid tile_types are
             `quadkeys`, `web`, `tms` and `here`.
        """
        if tile_type in ("quadkeys", "web", "tms", "here"):
            features = self.api.get_space_tile(
                space_id=self._info["id"],
                tile_type=tile_type,
                tile_id=tile_id,
                tags=tags,
                clip=clip,
                params=params,
                selection=selection,
                skip_cache=skip_cache,
                clustering=clustering,
                clusteringParams=clustering_params,
                margin=margin,
                limit=limit,
            )
            for f in features["features"]:
                yield f
        else:
            raise ValueError("Invalid value for parameter tile_type")

    def spatial_search(
        self,
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
    ) -> Generator[Feature, None, None]:
        """
        Get features with radius search.

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
        :yields: A Feature object.
        """
        features = self.api.get_space_spatial(
            space_id=self._info["id"],
            lat=lat,
            lon=lon,
            ref_space_id=ref_space_id,
            ref_feature_id=ref_feature_id,
            radius=radius,
            tags=tags,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
        )
        for f in features["features"]:
            yield f

    def spatial_search_geometry(
        self,
        data: dict,
        radius: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
        divide: Optional[bool] = False,
        cell_width: Optional[float] = None,
        units: Optional[str] = "m",
        chunk_size: int = 1,
    ) -> Generator[Feature, None, None]:
        """
        Search features which intersect the provided geometry.

        :param data: A JSON object which is getting used for the spatial search.
        :param radius: An int which defines the diameter(meters) of the search request.
        :param tags: A list of strings holding tag values.
        :param limit: A max. number of features to return in the result.
        :param params: A dict holding the HTTP query parameters.
        :param selection: A list of strings holding properties values.
        :param skip_cache: A Boolean if set to ``True`` the response is not returned from
            cache.
        :param divide: To divide geometry if the resultant features count is large.
        :param cell_width: Width of each cell in which geometry is to be divided
            in units specified, default values is meters.
        :param units: Unit for cell_width please refer,
            https://github.com/omanges/turfpy/blob/master/measurements.md#units-type
        :param chunk_size: Number of chunks each process to handle. The default value is
            1, for a large number of features please use `chunk_size` greater than 1
            to get better results in terms of performance.
        :yields: A Feature object.
        """
        if not divide:
            features = self.api.post_space_spatial(
                space_id=self._info["id"],
                data=data,
                radius=radius,
                tags=tags,
                limit=limit,
                params=params,
                selection=selection,
                skip_cache=skip_cache,
            )
            for f in features["features"]:
                yield f
        else:
            divide_features = divide_bbox(
                Feature(geometry=data), cell_width, units
            )
            manager = Manager()
            feature_list: List[dict] = manager.list()

            logger.info(
                f"Total number of features after division {len(divide_features)}"
            )
            part_func = partial(
                self._spatial_search_geometry,
                feature_list=feature_list,
                radius=radius,
                tags=tags,
                limit=limit,
                params=params,
                selection=selection,
                skip_cache=skip_cache,
            )

            with concurrent.futures.ProcessPoolExecutor() as executor:
                for f in executor.map(
                    part_func, divide_features, chunksize=chunk_size
                ):
                    pass

            for f in feature_list:
                yield f

    def _spatial_search_geometry(
        self,
        data: dict,
        feature_list: List[dict],
        radius: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        params: Optional[dict] = None,
        selection: Optional[List[str]] = None,
        skip_cache: Optional[bool] = None,
    ):
        features = self.api.post_space_spatial(
            space_id=self._info["id"],
            data=data["geometry"],
            radius=radius,
            tags=tags,
            limit=limit,
            params=params,
            selection=selection,
            skip_cache=skip_cache,
        )

        if features["features"]:
            feature_list.extend(features["features"])

    def add_features_geojson(
        self,
        path: str,
        encoding: str = "utf-8",
        features_size: int = 2000,
        chunk_size: int = 1,
    ):
        """
        Add features in space from a GeoJSON file.

        As API has a limitation on the size of features, features are divided into chunks,
        and multiple processes will process those chunks.
        Each chunk has a number of features based on the value of ``features_size``.
        Each process handles chunks based on the value of ``chunk_size``.

        :param path: Path to the GeoJSON file.
        :param encoding: A string to represent the type of encoding.
        :param features_size: An int representing a number of features to upload at
            a time.
        :param chunk_size: Number of chunks for each process to handle. The default value
            is 1, for a large number of features please use `chunk_size` greater than 1.
        :raises Exception: If GeoJSON file does not contain Feature or FeatureCollection.
        """
        with open(path, encoding=encoding) as f:
            features = json.load(f)

        if features["type"] == "Feature":
            if "id" not in features:
                raise Exception("Feature should have a id attribute")
            self.add_feature(feature_id=features["id"], data=features)
        elif features["type"] == "FeatureCollection":
            self.add_features(
                features, features_size=features_size, chunk_size=chunk_size
            )
        else:
            raise Exception(
                "The geojson file should contain either Feature or FeatureCollection"
            )

    def add_features_csv(
        self,
        path: str,
        lon_col: str,
        lat_col: str,
        id_col: str,
        alt_col: str = "",
        delimiter: str = ",",
    ):
        """
        Add features in space from a csv file.

        :param path: Path to csv file.
        :param lon_col: Name of the column for longitude coordinates.
        :param lat_col: Name of the column for latitude coordinates.
        :param id_col: Name of the column for feature id's.
        :param alt_col: Name of the column for altitude, if not provided
            altitudes with default value 0.0 will be added.
        :param delimiter: delimiter which should be used to process the csv file.
        :raises Exception: If values of params `lat_col`, `lon_col`, `id_col`
             do not match with column names in csv file.
        """
        feature: dict = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0, 0]},
            "properties": {},
        }
        with open(path) as f:
            input_file = csv.DictReader(f, delimiter=delimiter)
            columns = input_file.fieldnames
            if (
                lon_col not in columns  # type: ignore
                or lat_col not in columns  # type: ignore
                or id_col not in columns  # type: ignore
                or (alt_col not in columns if alt_col else False)  # type: ignore
            ):
                raise Exception(
                    "The longitude, latitude coordinates and id column name "
                    "should match with `lon_col`, `lat_col`,"
                    " `id_col` and `alt_col` parameter value"
                )
            for row in input_file:
                feature["geometry"]["coordinates"] = [
                    row[lon_col],
                    row[lat_col],
                    row[alt_col] if alt_col else 0.0,
                ]
                for field in columns:  # type: ignore
                    if (
                        field != lon_col
                        and field != lat_col
                        and field != id_col
                    ):
                        feature["properties"][field] = row[field]
                self.add_feature(feature_id=row[id_col], data=GeoJSON(feature))

    def cluster(
        self, clustering: str, clustering_params: Optional[dict] = None,
    ) -> dict:
        """
        Apply clustering algorithm for the space data.

        :param clustering: Name of the clustering algorithm.
            Available values : hexbin, quadbin
        :param clustering_params: Parameters for the clustering algorithm.
            Please refer : https://www.here.xyz/api/devguide/usingclustering/
        :return: GeoJSON.
        :raises Exception: If bounding box is not present in space statistics.

        Example:

        >>> from xyzspaces import XYZ
        >>> xyz = XYZ(credentials="XYZ_TOKEN")
        >>> space = xyz.spaces.from_id(space_id="existing-space-id")
        >>> space.cluster(clustering="hexbin")
        """
        statistics = self.get_statistics()
        bbox = statistics["bbox"]["value"]
        if len(bbox) == 0:
            raise Exception("Bounding box cannot be generated for the space")
        return self.api.get_space_bbox(
            space_id=self._info["id"],
            bbox=[bbox[0], bbox[1], bbox[2], bbox[3]],
            clustering=clustering,
            clusteringParams=clustering_params,
        )

    def isshared(self) -> bool:
        """Return the shared status of the space.

        :return: A boolean to indicate shared status of the space.
        """
        return True if "shared" in self.info else False

    def add_features_shapefile(
        self, path: str, features_size: int = 2000, chunk_size: int = 1
    ):
        """Upload shapefile to the space.

        :param path: A string representing full path of the shapefile. For zipped
            shapefile prepend ``zip://`` before path of shapefile.
        :param features_size: An int representing a number of features to upload at
            a time.
        :param chunk_size: Number of chunks for each process to handle. The default value
            is 1, for a large number of features please use `chunk_size` greater than 1.

        Example:
        >>> from xyzspaces import XYZ
        >>> xyz = XYZ(credentials="XYZ_TOKEN")
        >>> space = xyz.spaces.from_id(space_id="existing-space-id")
        >>> space.add_features_shapefile(path="shapefile.shp")
        """
        gdf = gpd.read_file(path)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            gdf.to_file(temp.name, driver="GeoJSON")
        self.add_features_geojson(
            path=temp.name, features_size=features_size, chunk_size=chunk_size
        )

    def add_features_wkt(self, path: str):
        """
        To upload data from wkt file to a space

        :param path: Path to wkt file
        """
        with open(path) as f:
            wkt_data = f.read()
            geojson_data = wkt_to_geojson(wkt_data)
            if geojson_data["type"] == "FeatureCollection":
                self.add_features(features=geojson_data)
            else:
                self.add_feature(data=geojson_data)

    def add_features_gpx(
        self, path: str, features_size: int = 2000, chunk_size: int = 1
    ):
        """Upload data from gpx file to the space.

        :param path: A string representing full path of the gpx file.
        :param features_size: An int representing a number of features to upload at
            a time.
        :param chunk_size: Number of chunks for each process to handle. The default value
            is 1, for a large number of features please use `chunk_size` greater than 1.
        """
        layers = fiona.listlayers(path)
        for layer in layers:
            gdf = gpd.read_file(path, driver="GPX", layer=layer)
            if gdf.empty:
                logger.debug(f"Empty Layer: {layer}")
                continue
            else:
                with tempfile.NamedTemporaryFile() as temp:
                    gdf.to_file(temp.name, driver="GeoJSON")
                    self.add_features_geojson(
                        path=temp.name,
                        features_size=features_size,
                        chunk_size=chunk_size,
                    )
