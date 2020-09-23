.. xyzspaces documentation master file, created by
   sphinx-quickstart on Wed Aug  5 16:59:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for xyzspaces
===========================

Manage your `XYZ Hub`_ or `HERE Data Hub`_ spaces from Python.

XYZ is an Open Source, real-time, cloud database system providing access to large geospatial data at scale.
An XYZ "Hub" manages "spaces" that contain "features" (geodata "records") with tags and properties, with spaces and features having unique IDs.
A RESTful API exists to provide low-level access to interact with a XYZ Hub.

This Python package allows to interact with your XYZ spaces and features on a given Hub using a higher level programmatic interface that wraps the RESTful API.
Using this package you can:

* Create, read, list, update, share, delete spaces (also: get space info and stats).
* Add, read, update, iterate, search, cluster (hex/quad bins), delete features.
* Search features by ID, tag, property, bbox, tile, radius, geometry.

Based on the XYZ Hub the HERE Data Hub is a commercial service (with a free plan), that offers some additional features (in a pro plan), like clustering, virtual spaces, activity logs, schema validation, rule based tagging and likely more to come.

.. _XYZ Hub: https://github.com/heremaps/xyz-hub
.. _HERE Data Hub: https://developer.here.com/products/data-hub

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

.. toctree::
  :maxdepth: 1
  :caption: Developer

  Contributing to xyzspaces <contributing>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
