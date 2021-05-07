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

"""Module for providing test fixtures for the Project API tests."""

import uuid

import pytest

from xyzspaces.apis import ProjectApi
from xyzspaces.config.default import XYZConfig


@pytest.fixture()
def api():
    """Create shared XYZ Project Api instance as a pytest fixture."""
    api = ProjectApi(config=XYZConfig.from_default())
    return api


@pytest.fixture()
def project_id():
    """Create shared XYZ project as a pytest fixture."""
    api = ProjectApi()

    # setup, create temporary project
    project = api.post_project(
        data={
            "title": "Testing xyzspaces",
            "description": "Temporary project.",
        }
    )
    project_id = project["id"]

    yield project_id

    # now teardown (delete temporary project)
    api.delete_project(project_id=project_id)


@pytest.fixture()
def create_projects(api):
    """Create a fixture to be used for creating temporary projects."""
    project_ids = []
    for i in range(5):
        data = dict(
            id=f"temp_project_{uuid.uuid4().urn[9:]}",
            title=f"My temp_project_{i}",
            description=f"temporary project for testing: {i}",
            status="UNPUBLISHED",
        )
        project = api.post_project(data=data)
        project_id = project["id"]
        project_ids.append(project_id)
    yield project_ids
    # tear down deleting all temp projects
    for project_id in project_ids:
        api.delete_project(project_id=project_id)
