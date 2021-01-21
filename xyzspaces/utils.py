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
This is a collection of utilities for using XYZ Hub.

Actually, they are almost unspecific to any XYZ Hub functionality, apart
from :func:`feature_to_bbox`, but convenient to use.
"""
import logging
import math
import os
import warnings
from itertools import zip_longest
from typing import List, Optional

import geopandas as gpd
from geojson import Feature, FeatureCollection, Point, Polygon
from shapely import geometry, wkt
from turfpy.measurement import bbox, bbox_polygon, distance, length
from turfpy.transformation import intersect

logger = logging.getLogger(__name__)


def join_string_lists(**kwargs) -> dict:
    """Convert named lists of strings to one dict with comma-separated strings.

    :param kwargs: Lists of strings
    :return: Converted dict.

    Example:

    >>> join_string_lists(foo=["a", "b", "c"], bar=["a", "b"], foobar=None)
    {"foo": "a,b,c", "bar": "a,b"}
    """
    return {k: ",".join(v) for k, v in kwargs.items() if v}


# TODO: Check if this is not also provided by geojson package...
#       Almost: list(geojson.coords(obj)
#       This should also be a field in feature JSON blob...
def feature_to_bbox(feature: dict) -> List[float]:
    """Extract bounding box from GeoJSON feature rectangle.

    :param feature: A dict representing a GeoJSON feature.
    :return: A list of four floats representing West, South, East and North
        margins of the resulting bounding box.
    """
    coords = feature["geometry"]["coordinates"][0]
    if len(coords) == 5:
        assert coords[-1] == coords[0]
        del coords[-1]

    p0, p1 = coords[0], coords[1]
    w, s, e, n = p0[0], p0[1], p1[0], p1[1]
    # unpacking lon, lat, alt in single variable c to avoid issues when alt is
    # missing in GeoJSON lon = c[0], lat = c[1], alt = c[2]
    for c in coords[1:]:
        if c[0] < w:
            w = c[0]
        if c[0] > e:
            e = c[0]
        if c[1] < s:
            s = c[1]
        if c[1] > n:
            n = c[1]

    return [w, s, e, n]


def get_xyz_token() -> str:
    """
    Read and return the value of the environment variable ``XYZ_TOKEN``.

    :return: The string value of the environment variable or an empty string
        if no such variable could be found.
    """
    xyz_token = os.environ.get("XYZ_TOKEN")
    if xyz_token is None:
        warnings.warn("No token found in environment variable XYZ_TOKEN.")

    return xyz_token or ""


def grouper(size, iterable, fillvalue=None):
    """
    Create groups of `size` each from given iterable.

    :param size: An int representing size of each group.
    :param iterable: An iterable.
    :param fillvalue: Value to put for the last group.
    :return: A generator.
    """
    args = [iter(iterable)] * size
    return zip_longest(fillvalue=fillvalue, *args)


def wkt_to_geojson(wkt_data: str) -> dict:
    """
    Converts wkt to geojson

    :param wkt_data: wkt data to be converted
    :return: Geojson
    """
    parsed_wkt = wkt.loads(wkt_data)

    geo = geometry.mapping(parsed_wkt)

    if geo["type"] == "GeometryCollection":
        feature_collection = []
        for g in geo["geometries"]:
            feature = Feature(geometry=g)
            feature_collection.append(feature)
        return FeatureCollection(feature_collection)
    else:
        return Feature(geometry=geo)


def grid(bbox, cell_width, cell_height, units):
    """
    This function generates the grids for the given bounding box

    :param bbox: bounding box coordinates
    :param cell_width: Cell width in specified in units
    :param cell_height: Cell height in specified in units
    :param units: Units for given sizes
    :return: FeatureCollection of grid boxes genarated
        for the giving bounding box
    """
    results = []
    west = bbox[0]
    south = bbox[1]
    east = bbox[2]
    north = bbox[3]

    start = Feature(geometry=Point((west, south)))
    end = Feature(geometry=Point((east, south)))
    x_fraction = cell_width / (distance(start, end, units))
    cell_width_deg = x_fraction * (east - west)

    start = Feature(geometry=Point((west, south)))
    end = Feature(geometry=Point((west, north)))
    y_fraction = cell_height / (distance(start, end, units))
    cell_height_deg = y_fraction * (north - south)

    # rows & columns
    bbox_width = east - west
    bbox_height = north - south
    columns = math.ceil(bbox_width / cell_width_deg)
    rows = math.ceil(bbox_height / cell_height_deg)

    # if the grid does not fill the bbox perfectly, center it.
    delta_x = (bbox_width - columns * cell_width_deg) / 2
    delta_y = (bbox_height - rows * cell_height_deg) / 2

    # iterate over columns & rows
    current_x = west + delta_x
    for column in range(0, columns):
        current_y = south + delta_y
        for row in range(0, rows):
            cell_poly = Feature(
                geometry=Polygon(
                    [
                        [
                            [current_x, current_y],
                            [current_x, current_y + cell_height_deg],
                            [
                                current_x + cell_width_deg,
                                current_y + cell_height_deg,
                            ],
                            [current_x + cell_width_deg, current_y],
                            [current_x, current_y],
                        ]
                    ]
                )
            )
            results.append(cell_poly)

            current_y += cell_height_deg

        current_x += cell_width_deg

    return FeatureCollection(results)


def divide_bbox(
    feature: dict,
    cell_width: Optional[float] = None,
    units: Optional[str] = "m",
):
    """
    Divides the given feature into grid
    boxes as per given cell width

    :param feature: Feature to be divide in grid
    :param cell_width: Width of each grid boxs
    :param units: Units for the width of grid boxs
    :return: List of features in which
        the input feature is divided
    """
    bb = bbox(feature)
    bbox_polygon_feature = bbox_polygon(bb)

    if not cell_width:
        gr = grid(
            bb,
            length(bbox_polygon_feature, units=units) / 4,
            length(bbox_polygon_feature, units=units) / 4,
            units,
        )
    else:
        gr = grid(bb, cell_width, cell_width, units)

    final = []
    for f in gr["features"]:
        try:
            inter = intersect([f, feature])
            if inter:
                final.append(inter)
        except Exception:
            logger.debug("The intersection geometry is incorrect")
    return final


def flatten_geometry(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Flatten the geometries in the given GeoPandas dataframe.
    Flatten geometry is formed by extracting individual geometries from
    GeometryCollection, MultiPoint, MultiLineString, MultiPolygon.

    :param data: GeoPandas dataframe to be flatten
    :return: Flat GeoPandas dataframe
    """
    geometry = data.geometry

    flattened_geometry = []

    flattened_gdf = gpd.GeoDataFrame()

    for geom in geometry:
        if geom.type in [
            "GeometryCollection",
            "MultiPoint",
            "MultiLineString",
            "MultiPolygon",
        ]:
            for subgeom in geom:
                flattened_geometry.append(subgeom)
        else:
            flattened_geometry.append(geom)

    flattened_gdf.geometry = flattened_geometry

    return flattened_gdf
