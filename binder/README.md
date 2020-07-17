# Docker Prerequisites

In order to run XYZ Spaces for Python using `jupyter-repo2docker` you will need to include all dependencies listed below in a file named `requirements.txt`:

```
# Core
geojson
requests

# Development
coverage
black
isort
mypy
pytest
pytest-cov
pytest-mypy

# Visualization
ipyleaflet
ipywidgets==7.5.1
jupyterlab==1.1.4
sidecar
```
