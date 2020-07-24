# XYZ Spaces for Python
[![Build Status](https://travis-ci.com/heremaps/xyz-spaces-python.svg?branch=master)](https://travis-ci.com/github/heremaps/xyz-spaces-python)
![PyPI](https://img.shields.io/pypi/v/xyzspaces)
![PyPI - Status](https://img.shields.io/pypi/status/xyzspaces)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xyzspaces)
[![Downloads](https://pepy.tech/badge/xyzspaces)](https://pepy.tech/project/xyzspaces)
[![Documentation Status](https://readthedocs.org/projects/docs/badge/?version=latest)](https://xyz-spaces-python.readthedocs.io/en/latest/)
![PyPI - License](https://img.shields.io/pypi/l/xyzspaces)
![GitHub contributors](https://img.shields.io/github/contributors/heremaps/xyz-spaces-python)


This package allows you to use your [XYZ Hub](https://github.com/heremaps/xyz-hub) server or [HERE Data Hub](https://developer.here.com/products/data-hub) from Python.

The image below is what you get when running the notebook in [docs/notebooks/demo.ipynb](./docs/notebooks/demo.ipynb),
which demonstrates how to use some features of the XYZ Hub's RESTful API to:

- create an XYZ space
- add features from a [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) file
- extract a single feature as a whole or within some bounding box (with and without clipping)
- delete the XYZ space

The example GeoJSON file is fetched from a third-party [GitHub account](https://github.com/johan/world.geo.json) and is rendered using [Leaflet](https://leafletjs.com) for simplicity.

# ![Example map from xyzspaces demo.ipynb notebook](https://user-images.githubusercontent.com/30625612/88389592-63d6be00-cdd4-11ea-903b-15c7819d7e13.png)


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

This package can be installed with `pip` from various sources:

- Install from its source repository on GitHub:

    ```bash
    pip install -e git+https://github.com/heremaps/xyz-spaces-python#egg=xyzspaces
    ```

- Install from the [Python Package Index](https://pypi.org/project/xyzspaces/):

    ```bash
    pip install xyzspaces
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

See the next section for how to run the test suite.

## Test Suite

You can run the test suite locally:

```bash
pip install -r requirements_dev.txt
pytest -v --cov=xyzspaces tests
```

The test suite provides test coverage of around 90% (but less if the tests cannot find your credentials).

## Documentation

For now, the documentation consists of a small number of example Jupyter notebooks in the [docs/notebooks](./docs/notebooks) directory plus an [API reference](https://xyz-spaces-python.readthedocs.io/en/latest/index.html), which is automatically generated from the docstrings in the code.

### Jupyter Notebooks

See [docs/notebooks/README.md](./docs/notebooks/README.md) to learn how to install and use the example Jupyter notebooks.

### API Reference

To generate the API reference locally in `docs/apiref/_build/html` run this command:

```bash
bash scripts/build_apiref.sh
```

### Hello World Example

The following is a tiny "Hello World"-like example that you can run to have a successful first XYZ experience right after installation! Just make sure to use your own real XYZ token!

```python
import json
import xyzspaces as xyz
from geojson import FeatureCollection

xyz = xyz.XYZ(credentials="MY_XYZ_TOKEN")

# Creating a New Space
title = "My Demo Space"
description = "Description as markdown"
space = xyz.spaces.new(title=title, description=description)

# Add a Feature to a Space
features =  {
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

feature_id = space.add_features(features=FeatureCollection([features]))["features"][0]["id"]

# Reading a Feature from a Space
feature = space.get_feature(feature_id=feature_id)
print(json.dumps(feature, indent=4, sort_keys=True))
```

### Logging Configuration

Set the variable `XYZ_LOG_CONFIG` to hold the full path of the logging configuration options file `logging_config.json`:

```bash
export XYZ_LOG_CONFIG=~/logging_config.json
```

This ensures that log messages will be written to the file `xyz.log` in your current working directory.

Note that by default, only `error` messages are logged to the console.

Here is an example log file (`xyz.log`):

```text
2020-02-21 17:55:46,132 - apis.py:130 - ERROR - Curl command: curl --request GET https://xyz.api.here.com/hub/spaces/dummy-111 --header "Authorization: Bearer <XYZ_TOKEN>"
2020-02-21 17:55:46,133 - apis.py:131 - ERROR - Response status code: 404
2020-02-21 17:55:46,133 - apis.py:132 - ERROR - Response headers: {'Content-Type': 'application/json', 'Content-Length': '150', 'Connection': 'keep-alive', 'Date': 'Fri, 21 Feb 2020 12:25:46 GMT', 'x-amzn-RequestId': '397c8039-79f1-4956-bbe4-46ca78c7ec2d', 'content-encoding': 'gzip', 'Stream-Id': '397c8039-79f1-4956-bbe4-46ca78c7ec2d', 'x-amzn-Remapped-Content-Length': '150', 'x-amzn-Remapped-Connection': 'keep-alive', 'x-amz-apigw-id': 'IPzblGVFjoEF5pg=', 'x-amzn-Remapped-Date': 'Fri, 21 Feb 2020 12:25:46 GMT', 'X-Cache': 'Error from cloudfront', 'Via': '1.1 e25383e25378de918d3b187b3239eb5b.cloudfront.net (CloudFront)', 'X-Amz-Cf-Pop': 'BOM51-C2', 'X-Amz-Cf-Id': 'nZAJUB_FBiHdojziSoG3SBcMdf8rNyHuOMSlJljyxDNlx1I0O3t9YQ=='}
2020-02-21 17:55:46,134 - apis.py:133 - ERROR - Response text: {"type":"ErrorResponse","error":"Exception","errorMessage":"The requested resource does not exist.","streamId":"397c8039-79f1-4956-bbe4-46ca78c7ec2d"}
```

# License

Copyright (C) 2019-2020 HERE Europe B.V.

Unless otherwise noted in `LICENSE` files for specific directories, the [LICENSE](LICENSE) in the root applies to all content in this repository.
