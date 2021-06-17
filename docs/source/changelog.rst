CHANGELOG
=========

xyzspaces 0.6.0 (2021-06-17)
----------------------------

* **Features**

  * Added support custom base URL of Data Hub APIs for self-hosted Data Hub. (`#113 <https://github.com/heremaps/xyz-spaces-python/pull/113>`_)

  * Added support for launch datahub space invader. (`commit <https://github.com/heremaps/xyz-spaces-python/commit/6863eb479355ce659a2cab3c8aa5442868c3070e>`_)

  * Fixed feature_id gettting skipped from GeoPandas data.(`commit <https://github.com/heremaps/xyz-spaces-python/commit/52117691084c41e5aea27ae77a69a91148d178c3>`_)

xyzspaces 0.5.0 (2021-02-01)
----------------------------

* **Features**

  * Added functionality to ``clone`` Space. (`#93 <https://github.com/heremaps/xyz-spaces-python/pull/93>`_)
  * Handle HTTP 429 responses with ``backoff`` package. (`#95 <https://github.com/heremaps/xyz-spaces-python/pull/95>`_)
  * support the new ``force2D`` parameter for all the APIs used to read features. (`#96 <https://github.com/heremaps/xyz-spaces-python/pull/96>`_)
  * Add support for new mode and vizSampling params in HubApi.get_space_tile. (`#101 <https://github.com/heremaps/xyz-spaces-python/pull/101>`_)

* **Documentation**

  * Start collecting/documenting architecture decision records (ADRs). (`#90 <https://github.com/heremaps/xyz-spaces-python/pull/90>`_)
  * Add support for executable code in Sphinx documentation. (`#99 <https://github.com/heremaps/xyz-spaces-python/pull/99>`_)

* **Misc**

  * Migrated CI from Travis to GitHub Actions. (`#111 <https://github.com/heremaps/xyz-spaces-python/pull/111>`_)

xyzspaces 0.4.0 (2020-09-18)
----------------------------

* **Features**

  * Added feature to upload data from ``kml`` file to the space.(`#49 <https://github.com/heremaps/xyz-spaces-python/pull/49>`__)
  * Added ``limit`` param to method ``iter_feature`` to control numer of features to iterate in single call.(`#52 <https://github.com/heremaps/xyz-spaces-python/pull/52>`__)
  * Fixed encoding and projections issue for ``shapefile`` upload.(`#54 <https://github.com/heremaps/xyz-spaces-python/pull/54>`__)
  * Enabled property search while searching features in bounding box.(`#56 <https://github.com/heremaps/xyz-spaces-python/pull/56>`__)
  * Added feature to upload data from ``geobuff`` file to the space.(`#57 <https://github.com/heremaps/xyz-spaces-python/pull/57>`__)
  * Remove duplicate features for ``spatial_search_geometry`` with division(`#58 <https://github.com/heremaps/xyz-spaces-python/pull/58>`__)
  * Enabled property search while searching features in tile.(`#61 <https://github.com/heremaps/xyz-spaces-python/pull/61>`__)
  * Remove duplicate features while add to space using ``add_features`` and also added a ``mutation`` parameter to mutate input features or not.(`#64 <https://github.com/heremaps/xyz-spaces-python/pull/64>`__)
  * ``description`` is optional when creating the space.(`#68 <https://github.com/heremaps/xyz-spaces-python/pull/68>`__)
  * Added feature to upload data from ``Geopandas Dataframe`` file to the space.(`#71 <https://github.com/heremaps/xyz-spaces-python/pull/71>`__)
  * Enabled reading space data as Geopandas Dataframe.(`#72 <https://github.com/heremaps/xyz-spaces-python/pull/72>`__)
  * Improved performance of CSV upload.(`#77 <https://github.com/heremaps/xyz-spaces-python/pull/77>`__)
  * Improvement in the performance of ``add_features_geojson``.(`#79 <https://github.com/heremaps/xyz-spaces-python/pull/79>`__)
  * Changes to convert shape file with projection of different type to EPSG:4326.(`#83 <https://github.com/heremaps/xyz-spaces-python/pull/83>`__)

* **Documentation**

  * New notebook illustrating spatial search on MS US building footprints dataset.(`#62 <https://github.com/heremaps/xyz-spaces-python/pull/62>`__)

xyzspaces 0.3.2 (2020-08-19)
----------------------------

* **Features**

  * Added feature to upload data from ``shapefile`` to the space.(`#40 <https://github.com/heremaps/xyz-spaces-python/pull/40>`__)
  * Added feature to upload data from ``WKT`` file to the space.(`#41 <https://github.com/heremaps/xyz-spaces-python/pull/41>`__)
  * Added feature to upload data from ``gpx`` file to the space.(`#42 <https://github.com/heremaps/xyz-spaces-python/pull/42>`__)
  * Optimized the ``spatial search`` to search features from large geometries.(`#44 <https://github.com/heremaps/xyz-spaces-python/pull/44>`__)

* **Misc**

  * Added Binder support to the repository.(`#28 <https://github.com/heremaps/xyz-spaces-python/pull/28>`__)
  * Added **clientId** in query params of the Hub API requests.(`#36 <https://github.com/heremaps/xyz-spaces-python/pull/36>`__)
  * Updated ``__version__`` attribute now it can be used as ``from xyzspaces import __version__``.(`#38 <https://github.com/heremaps/xyz-spaces-python/pull/38>`__)

xyzspaces 0.3.1 (2020-07-24)
----------------------------

* **Misc**

  * Minor changes to README.(`0.3.1 <https://github.com/heremaps/xyz-spaces-python/releases/tag/0.3.1>`__)

xyzspaces 0.3.0 (2020-07-24)
----------------------------

* **Misc**

  * First public release.(`0.3.0 <https://github.com/heremaps/xyz-spaces-python/releases/tag/0.3>`__)
