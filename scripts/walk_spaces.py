#! /usr/bin/env python3

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
This tool "template" can help perform some maintenance work on XYZ spaces.

In its current form this only walks over all spaces available for the token
found in the environment variable XYZ_TOKEN and prints the space ID, number
of features inside and space title. It can be easily modified to perform
simple maintenance tasks like clean-up no longer needer XYZ spaces, etc.
"""

from xyzspaces.apis import HubApi


def walk_spaces():
    """Walk over all spaces and do something to them..."""
    # Uses credentials from XYZ_TOKEN env. variable.
    api = HubApi()

    for i, space in enumerate(api.get_spaces()):
        id, title = space["id"], space["title"]
        count = api.get_space_count(space_id=id)["count"]
        # if title.find("Testing") >= 0:
        # if count > 0:
        #     api.delete_space(space_id=id)
        print(i, id, count, title)


if __name__ == "__main__":
    walk_spaces()
