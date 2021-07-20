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

"""This is a preliminary collection of little tools that use XYZ."""

from typing import List, Optional

from .apis import HubApi
from .config.default import XYZConfig


def subset_geojson(
    gj: dict,
    config: Optional[XYZConfig] = None,
    bbox: Optional[List[float]] = None,
    tile_type: Optional[str] = None,
    tile_id: Optional[str] = None,
    clip: Optional[bool] = False,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: Optional[int] = None,
) -> dict:
    """Return a subset of the GeoJSON object inside some bbox or map tile or radius.

    This will create a temporary space, add the provided GeoJSON object,
    perform the bbox or tile subsetting and return the resulting GeoJSON
    object after deleting the temporary space again.

    :param config: An object of `class:XYZConfig`, If not provied
            ``XYZ_TOKEN`` will be used from environment variable and
            other configurations will be used as defined in :py:mod:`default_config`.
    :param gj: The GeoJSON data object.
    :param bbox: The bounding box described as a list of four numbers (its
        West, South, East, and North margins).
    :param tile_type: The tile type, for now one of: ...
    :param tile_id: The tile ID, a string composed of digits to identify
        the tile according to the specified tile type.
    :param clip: A Boolean to indicate if the features should be clipped
        at the tile or bbox.
    :param lat: A float to represent latitude.
    :param lon: A float to represent longitude.
    :param radius: An int in meter which defines the diameter of the search request.
        Should be provided  with ``lat`` and ``lon`` for spatial search.
    :returns: A GeoJSON object covering the desired tile or bbox subset of
        the original GeoJSON object.
    :raises ValueError: If the wrong combination of ``bbox``, ``tile_type``
        and ``tile_id``, ``lat`` and ``lon`` was provided.
    """
    if bbox and (tile_type or tile_id):
        raise ValueError("The bbox cannot be provided together with tile ID/type.")
    elif bbox and (lat or lon):
        raise ValueError("The bbox cannot be provided together with lat and lon.")
    elif (tile_type or tile_id) and (lat or lon):
        raise ValueError(
            "The tile_id and tile_type cannot be provided together with " "lat and lon."
        )
    if not bbox:
        assert (tile_type and tile_id) or (
            lat and lon
        ), "Tile ID and type or lat and lon must be provided."
    if bbox:
        assert len(bbox) == 4

    api = HubApi(config=config if config else XYZConfig.from_default())

    # Create space.
    res = api.post_space(data=dict(title="Tile GeoJSON", description="Temporary space."))
    space_id = res["id"]

    # Add features.
    api.put_space_features(space_id=space_id, data=gj)

    if bbox:
        tiled = api.get_space_bbox(space_id=space_id, bbox=bbox, clip=clip)
    elif tile_type and tile_id:
        tiled = api.get_space_tile(
            space_id=space_id, tile_type=tile_type, tile_id=tile_id, clip=True
        )
    elif lat and lon:
        tiled = api.get_space_spatial(space_id=space_id, lat=lat, lon=lon, radius=radius)

    # Delete space.
    api.delete_space(space_id=space_id)

    return tiled
