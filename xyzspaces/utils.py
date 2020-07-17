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
This is a collection of utilities for using XYZ Hub.

Actually, they are almost unspecific to any XYZ Hub functionality, apart
from :func:`feature_to_bbox`, but convenient to use.
"""

import os
import warnings
from itertools import zip_longest
from typing import List


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
    for lon, lat, alt in coords[1:]:
        if lon < w:
            w = lon
        if lon > e:
            e = lon
        if lat < s:
            s = lat
        if lat > n:
            n = lat

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
