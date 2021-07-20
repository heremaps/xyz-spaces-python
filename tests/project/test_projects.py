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

"""Module for testing HERE XYZ Project API endpoints."""


import pytest

from xyzspaces.apis import ProjectApi
from xyzspaces.utils import get_xyz_token

XYZ_TOKEN = get_xyz_token()


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_projects(api):
    """Test get projects list."""
    projects = api.get_projects()
    assert type(projects) == list


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_projects_env_token():
    """Test get projects list with default token directly from environment."""
    my_api = ProjectApi()
    projects = my_api.get_projects()
    assert type(projects) == list


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_project(api, project_id):
    """Test get single project."""
    project = api.get_project(project_id=project_id)
    print(project)
    exp = set(
        [
            "id",
            "status",
            # 'rot', 'base', 'meta', 'layers', 'bookmarks',
            # 'thumbnail', 'created_at', 'last_update', 'map_settings',
            # 'publish_settings'
        ]
    )
    assert exp.issubset(set(project.keys()))


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def _test_get_my_project(api, project_id):
    """Test get single project."""
    # https://xyz.here.com/studio/project/5c54716d-f900-4b89-80ac-b21518e94b30
    project = api.get_project(project_id="5c54716d-f900-4b89-80ac-b21518e94b30")
    print(project)


# This is tested inside the roundtrip test below.
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def _test_post_project(api):
    """Test post new project."""
    data = dict(
        id="temp-project-1",
        title="My temp-project-1",
        description="Temporary project for test purposes.",
        status="UNPUBLISHED",
    )
    project = api.post_project(data=data)
    exp = set(["id", "description", "status", "created_at", "last_update"])
    assert exp == set(project.keys())


# This is tested inside the roundtrip test below.
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def _test_delete_project(api):
    """Test delete new project."""
    response = api.delete_project(project_id="temp-project-1")
    assert response == ""


# @pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_roundtrip_project(api):
    """Test create/update/delete project."""
    data = dict(
        # id=project_id,
        description="Temporary project for test purposes.",
        status="UNPUBLISHED",
    )
    project = api.post_project(data=data)
    project_id = project["id"]
    exp = set(["id", "description", "status"])
    assert exp.issubset(set(project.keys()))

    project = api.put_project(project_id=project_id, data={})
    assert "description" not in set(project.keys())

    data = dict(description="Temporary project (after put and patch).")
    project = api.patch_project(project_id=project_id, data=data)
    assert "description" in set(project.keys())

    response = api.delete_project(project_id=project_id)
    assert response == ""


@pytest.mark.skipif(not XYZ_TOKEN, reason="No token found.")
def test_get_projects_by_pagination(api, create_projects):
    """
    Test get multiple projects based on ``paginate``, ``limit`` and ``handle`` params.

    The ``limit`` parameter will limit number of projects returned by
    ``ProjectApi.get_projects`` method.

    :param api: A pytest fixture which will return :class:`ProjectApi` object.
    :param create_projects: A pytest fixture that will return list of project_ids.
    """
    # Added assert below to just check fixture has return list of project ids.
    assert type(create_projects) == list
    my_api = ProjectApi()
    limit_projects = my_api.get_projects(paginate=True, limit=2)
    assert type(limit_projects) == dict
    assert len(limit_projects["projects"]) == 2
    assert type(limit_projects["handle"]) == int

    handle = limit_projects["handle"]
    projs = my_api.get_projects(paginate=True, limit=3, handle=handle)
    assert type(projs) == dict
    assert len(projs["projects"]) == 3
    assert type(projs["handle"]) == int
