# XYZ Spaces for Python

[![Documentation Status](https://img.shields.io/readthedocs/xyz-spaces-python?logo=read-the-docs)](https://xyz-spaces-python.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/heremaps/xyz-spaces-python.svg?branch=master)](https://travis-ci.com/github/heremaps/xyz-spaces-python)
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
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/heremaps/xyz-spaces-python/master?urlpath=lab/tree/docs/notebooks)

Manage your [XYZ Hub](https://github.com/heremaps/xyz-hub) or [HERE Data Hub](https://developer.here.com/products/data-hub) spaces from Python.

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

- A Python installation, 3.6+ recommended, with the `pip` command available to install dependencies
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
  
## Documentation

Documentation is hosted [here](https://xyz-spaces-python.readthedocs.io/en/latest/index.html).

To build the docs locally run:

```bash
bash scripts/build_docs.sh
```

### Hello World Example

The following is a tiny "Hello World"-like example that you can run to have a successful first XYZ experience right after installation! Just make sure to use your own real XYZ token!

```python
import geojson
import xyzspaces

xyz = xyzspaces.XYZ(credentials="MY_XYZ_TOKEN")

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

# License

Copyright (C) 2019-2020 HERE Europe B.V.

Unless otherwise noted in `LICENSE` files for specific directories, the [LICENSE](https://github.com/heremaps/xyz-spaces-python/blob/master/LICENSE) in the root applies to all content in this repository.
