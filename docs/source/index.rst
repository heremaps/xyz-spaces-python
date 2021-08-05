.. xyzspaces documentation master file, created by
   sphinx-quickstart on Wed Aug  5 16:59:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===========================
Documentation for xyzspaces
===========================

Manage your `XYZ Hub`_ or `HERE Data Hub`_ spaces and `Interactive Map Layer`_ from Python.

Data Hub
========

XYZ is an Open Source, real-time, cloud database system providing access to large geospatial data at scale.
An XYZ "Hub" manages "spaces" that contain "features" (geodata "records") with tags and properties, with spaces and features having unique IDs.
A RESTful API exists to provide low-level access to interact with a XYZ Hub.

This Python package allows to interact with your XYZ spaces and features on a given Hub using a higher level programmatic interface that wraps the RESTful API.
Using this package you can:

* Create, read, list, update, share, delete spaces (also: get space info and stats).
* Add, read, update, iterate, search, cluster (hex/quad bins), delete features.
* Search features by ID, tag, property, bbox, tile, radius, geometry.

Based on the XYZ Hub the HERE Data Hub is a commercial service (with a free plan), that offers some additional features (in a pro plan), like clustering, virtual spaces, activity logs, schema validation, rule based tagging and likely more to come.

Interactive Map Layers
======================

The ``xyzspaces`` package supports Interactive Map Layers which is Data Hub on `HERE Platform <https://platform.here.com/>`_.
Using ``xyzspaces`` you can interact with your Interactive Map Layers using higher level pythonic interface that wraps the RESTful API.
With Interactive Map Layers, data is stored in GeoJSON and can be retrieved dynamically at any zoom level.
Interactive map layer is optimized for the visualization, analysis, and modification of data on a map (i.e., GIS functions).

Key features of Interactive Map Layers include:

* Creating and modifying maps manually or programmatically; edits are published real-time and require no additional interaction.

* Modifying data a granular feature and feature property level.

* Adding and removing points, lines, and polygons directly on a map.

* Ability to retrieve data in different tiling schemes.

* Exploring and retrieving data by feature ID, bounding box, spatial search, property search, and features contained within a tile.

* Searching for data by values of feature properties (e.g., speed limits, type of place, address, name, etc.).

* Data sampling, making it possible to efficiently render an excerpt of a very large data set for visual reference and analysis.

* Clustering using hexbins or quadbins to produce rich, visual data representations.


.. _XYZ Hub: https://github.com/heremaps/xyz-hub
.. _HERE Data Hub: https://developer.here.com/products/data-hub
.. _Interactive Map Layer: https://developer.here.com/documentation/data-user-guide/user_guide/portal/layers/layers.html

.. toctree::
  :maxdepth: 1
  :caption: Getting Started

  Prerequisites <prerequisites>
  Installation <install>

.. toctree::
  :maxdepth: 1
  :caption: User Guide

  Examples <examples>
  API Reference <xyzspaces>
  Logging <logging>

.. toctree::
  :maxdepth: 1
  :caption: Reference Guide

  Tests <tests>
  Changelog <changelog>
  Blogs and Talks <blogs_talks>

.. toctree::
  :maxdepth: 1
  :caption: Developer

  Contributing to xyzspaces <contributing>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
