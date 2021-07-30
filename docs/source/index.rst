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

Interactive Map Layer
=====================

The ``xyzspaces`` package also supports Interactive Map Layer(IML) which is Data Hub on `HERE Platform <https://platform.here.com/>`_.
Using ``xyzspaces`` you can interact with your Interactive Map Layer using higher level pythonic interface that wraps the RESTful API.
Using this package you can:

* Create, read, update, Interactive Map Layer (also: get Interactive Map Layer info and stats).
* Add, read, update, iterate, search, cluster (hex/quad bins), delete features.
* Search features by ID, tag, property, bbox, tile, radius, geometry.

Credentials
-----------
To interact with Interactive Map Layer you will need an account on the HERE Platform.
To get more details on the HERE Platform account please check `this <https://developer.here.com/documentation/identity-access-management/dev_guide/topics/obtain-user-credentials.html>`_.
Once you have the account follow the below steps to get credentials:

*  Go to `HERE Platform Applications and Keys <https://platform.here.com/profile/apps-and-keys>`_ and register a new app.

*  Create a key for the app and download the generated `credentials.properties` file.

* Place the credentials file into:

  For Linux/MacOS::

   $HOME/.here/credentials.properties

  For Windows::

   %USERPROFILE%\.here\credentials.properties

The HERE platform generated app credentials should look similar to the example below::

   here.user.id = <example_here>
   here.client.id = <example_here>
   here.access.key.id = <example_here>
   here.access.key.secret = <example_here>
   here.token.endpoint.url = <example_here>

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
