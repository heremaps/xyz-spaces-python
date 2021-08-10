# XYZ Spaces for Python

[![Documentation Status](https://img.shields.io/readthedocs/xyz-spaces-python?logo=read-the-docs)](https://xyz-spaces-python.readthedocs.io/en/latest/?badge=latest)
![Tests](https://github.com/heremaps/xyz-spaces-python/workflows/Tests/badge.svg)
[![PyPI - Status](https://img.shields.io/pypi/status/xyzspaces)](https://pypi.org/project/xyzspaces/)
[![PyPI - Python Version](https://img.shields.io/pypi/v/xyzspaces.svg?logo=pypi)](https://pypi.org/project/xyzspaces/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/xyzspaces)](https://pypi.org/project/xyzspaces/)
[![Downloads](https://pepy.tech/badge/xyzspaces)](https://pepy.tech/project/xyzspaces)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/xyzspaces?logo=conda-forge)](https://anaconda.org/conda-forge/xyzspaces)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/xyzspaces)](https://anaconda.org/conda-forge/xyzspaces)
[![PyPI - License](https://img.shields.io/pypi/l/xyzspaces)](https://pypi.org/project/xyzspaces/)
[![LGTM alerts](https://img.shields.io/lgtm/alerts/g/heremaps/xyz-spaces-python.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/heremaps/xyz-spaces-python/alerts/)
[![LGTM context](https://img.shields.io/lgtm/grade/python/g/heremaps/xyz-spaces-python.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/heremaps/xyz-spaces-python/context:python)
[![Swagger Validator](https://img.shields.io/swagger/valid/3.0?specUrl=https%3A%2F%2Fxyz.api.here.com%2Fhub%2Fstatic%2Fopenapi%2Fstable.yaml)](https://xyz.api.here.com/hub/static/swagger/)
[![GitHub contributors](https://img.shields.io/github/contributors/heremaps/xyz-spaces-python)](https://github.com/heremaps/xyz-spaces-python/graphs/contributors)
[![Codecov](https://codecov.io/gh/heremaps/xyz-spaces-python/branch/master/graph/badge.svg)](https://codecov.io/gh/heremaps/xyz-spaces-python)
[![Slack](https://img.shields.io/badge/heredev-datahub-00AFAA?logo=slack)](https://heredev.slack.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![commits since](https://img.shields.io/github/commits-since/heremaps/xyz-spaces-python/latest.svg)](https://github.com/heremaps/xyz-spaces-python/commits/master)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/xyzspaces/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/xyzspaces)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/heremaps/xyz-spaces-python/master?urlpath=lab/tree/docs/notebooks)

Manage your [XYZ Hub](https://github.com/heremaps/xyz-hub) or [HERE Data Hub](https://developer.here.com/products/data-hub) spaces  and [Interactive Map Layer](https://developer.here.com/documentation/data-user-guide/user_guide/portal/layers/layers.html) from Python.

<b>FEATURED IN: [Online Python Machine Learning Conference &amp; GeoPython 2020](http://2020.geopython.net/), Sept 21, 2020, see [conference schedule](http://2020.geopython.net/schedule.html).</b>


## Motivation

XYZ is an Open Source, real-time, cloud database system providing access to large geospatial data at scale. An XYZ "Hub" manages "spaces" that contain "features" (geodata "records") with tags and properties, with spaces and features having unique IDs. A RESTful API exists to provide low-level access to interact with a XYZ Hub.

This Python package allows to interact with your XYZ spaces and features on a given Hub using a higher level programmatic interface that wraps the RESTful API. Using this package you can:

- Create, read, list, update, share, delete spaces (also: get space info and stats).
- Add, read, update, iterate, search, cluster (hex/quad bins), delete features.
- Search features by ID, tag, property, bbox, tile, radius, geometry.

Based on the XYZ Hub the HERE Data Hub is a commercial service (with a free plan), that offers some additional features (in a pro plan), like clustering, virtual spaces, activity logs, and likely more to come.

The GIF below shows an interaction with an [example notebook](https://github.com/heremaps/xyz-spaces-python/blob/master/docs/notebooks/building_numbers.ipynb),
demonstrating how to use a spatial search on a big public dataset, loaded from the HERE [Data Hub](https://here.xyz).

# ![Example from xyzspaces building_numbers.ipynb notebook](https://github.com/heremaps/xyz-spaces-python/raw/master/images/building_numbers.gif)


## Prerequisites

Before you can install this package, run its test-suite or use the example notebooks to make sure your system meets the following prerequisities:

- A Python installation, 3.7+ recommended, with the `pip` command available to install dependencies
- A HERE developer account, free and available under [HERE Developer Portal](https://developer.here.com)
- An XYZ API access token from your XYZ Hub server or the [XYZ portal](https://www.here.xyz) (see also its [Getting
  Started](https://www.here.xyz/getting-started/) section) in an environment variable named `XYZ_TOKEN` which you can
  set like this (with a valid value, of course):

    ```bash
    export XYZ_TOKEN="MY-FANCY-XYZ-TOKEN"
    ```

    If you prefer, you can alternatively provide this token as a parameter in your code.

## Installation

This package can be installed with `pip` or `conda` from various sources:

- Install with conda from the Anaconda [conda-forge channel](https://anaconda.org/conda-forge/xyzspaces):

    ```bash
    conda install -c conda-forge xyzspaces
    ```

- Install from the [Python Package Index](https://pypi.org/project/xyzspaces/):

    ```bash
    pip install xyzspaces
    ```

- Install from its source repository on GitHub:

    ```bash
    pip install -e git+https://github.com/heremaps/xyz-spaces-python#egg=xyzspaces
    ```

If you want to run the test suite or experiment with the example notebooks bundled, you need to clone the whole repository:

- Make a local clone of the repository hosting this package. The following command should do:

    ```bash
    git clone https://github.com/heremaps/xyz-spaces-python.git
    ```

- Change into the repo root directory:

    ```bash
    cd xyzspaces
    ```
  
## Interactive Map Layers
The `xyzspaces` package supports Interactive Map Layers which is Data Hub on [HERE Platform](https://platform.here.com/).
Using `xyzspaces` you can interact with your Interactive Map Layers using higher level pythonic interface that wraps the RESTful API.
With Interactive Map Layers, data is stored in GeoJSON and can be retrieved dynamically at any zoom level. 
Interactive map layer is optimized for the visualization, analysis, and modification of data on a map (i.e., GIS functions).

Key features of Interactive Map Layers include:
- Creating and modifying maps manually or programmatically; edits are published real-time and require no additional interaction.
- Modifying data a granular feature and feature property level.
- Adding and removing points, lines, and polygons directly on a map.
- Ability to retrieve data in different tiling schemes.
- Exploring and retrieving data by feature ID, bounding box, spatial search, property search, and features contained within a tile.
- Searching for data by values of feature properties (e.g., speed limits, type of place, address, name, etc.).
- Data sampling, making it possible to efficiently render an excerpt of a very large data set for visual reference and analysis.
- Clustering using hexbins or quadbins to produce rich, visual data representations.

### Credentials
To interact with Interactive Map Layer you will need an account on the HERE Platform.
To get more details on the HERE Platform account please check our documentation [Get a HERE account](https://developer.here.com/documentation/identity-access-management/dev_guide/topics/obtain-user-credentials.html).
Once you have the account follow the below steps to get credentials:
- Go to [HERE Platform Applications and Keys](https://platform.here.com/profile/apps-and-keys) and register a new app.
- Create a key for the app and download the generated `credentials.properties` file.

The HERE platform generated app credentials should look similar to the example below:
```
  here.user.id = <example_here>
  here.client.id = <example_here>
  here.access.key.id = <example_here>
  here.access.key.secret = <example_here>
  here.token.endpoint.url = <example_here>
```

You can provide your credentials using any of the following methods:

- Default credentials
- Environment variables
- Credentials file

#### Default credentials
Place the credentials file into

For Linux/MacOS: `$HOME/.here/credentials.properties`

For Windows: `%USERPROFILE%\.here\credentials.properties`

#### Environment Variables

You can override default credentials by assigning values to the following environment variables:
```
HERE_USER_ID
HERE_CLIENT_ID
HERE_ACCESS_KEY_ID
HERE_ACCESS_KEY_SECRET
HERE_TOKEN_ENDPOINT_URL
```

#### Credentials File

You can specify any credentials file as an alternative to that found in `~/.here/credentials.properties`. An error is generated if there is no file present at the path, or if the file is not properly formatted.

  
## Documentation

Documentation is hosted [here](https://xyz-spaces-python.readthedocs.io/en/latest/index.html).

To build the docs locally run:

```bash
bash scripts/build_docs.sh
```

### Hello World Example

The following are tiny "Hello World"-like examples that you can run to have a successful first XYZ experience right after installation!

#### Data Hub
```python
import geojson
import os
import xyzspaces

os.environ["XYZ_TOKEN"] = "MY_XYZ_TOKEN"
xyz = xyzspaces.XYZ()

# Create a New Space
title = "My Demo Space"
description = "My Description"
space = xyz.spaces.new(title=title, description=description)

# Define a New Feature
feature =  {
    "type": "Feature",
    "properties": {"party": "Republican"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-104.05, 48.99],
            [-97.22,  48.98],
            [-96.58,  45.94],
            [-104.03, 45.94],
            [-104.05, 48.99]
        ]]
    }
}

# Save it to a Space and get its ID
feature_id = space.add_features(features=geojson.FeatureCollection([feature]))["features"][0]["id"]

# Read a Feature from a Space
feature = space.get_feature(feature_id=feature_id)
print(geojson.dumps(feature, indent=4, sort_keys=True))
```
#### Interactive Map Layer
```python
import geojson
from xyzspaces import IML
from xyzspaces.iml.credentials import Credentials

credentials = Credentials.from_default() # credentials are in either credentials file at default location or in environment variables

layer_details = {
    "id": "demo-interactive-layer",
    "name": "Demo Interactive Layer",
    "summary": "Demo Interactive Layer",
    "description": "Demo Interactive Layer",
    "layerType": "interactivemap",
    "interactiveMapProperties": {},
}

iml = IML.new(
    catalog_id="demo-catalog1",
    catalog_name="demo-catalog",
    catalog_summary="Demo catalog",
    catalog_description="Demo catalog",
    layer_details=layer_details,
    credentials=credentials,
)

# Define a New Feature
feature = {
    "type": "Feature",
    "properties": {"party": "Republican"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-104.05, 48.99],
                [-97.22, 48.98],
                [-96.58, 45.94],
                [-104.03, 45.94],
                [-104.05, 48.99],
            ]
        ],
    },
}
# Save feature to interactive map layer
iml.layer.write_feature(feature_id="demo_feature", data=feature)

# Read feature from nteractive map layer
resp = iml.layer.get_feature(feature_id="demo_feature")
print(geojson.dumps(resp.to_geojson(), indent=4, sort_keys=True))
```


# License

Copyright (C) 2019-2021 HERE Europe B.V.

Unless otherwise noted in `LICENSE` files for specific directories, the [LICENSE](https://github.com/heremaps/xyz-spaces-python/blob/master/LICENSE) in the root applies to all content in this repository.
