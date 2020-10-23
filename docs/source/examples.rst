Examples
========
The Jupyter `notebooks <https://github.com/heremaps/xyz-spaces-python/tree/master/docs/notebooks>`__ show various functionalities of xyzspaces.
You can directly play with examples by clicking on the binder button:

.. image:: https://mybinder.org/badge_logo.svg
  :target: https://mybinder.org/v2/gh/heremaps/xyz-spaces-python/master?urlpath=lab/tree/docs/notebooks

To run the example notebooks locally See `docs/notebooks/README.md <https://github.com/heremaps/xyz-spaces-python/blob/master/docs/notebooks/README.md>`__.

The GIF below shows an interaction with an example `notebook <https://github.com/heremaps/xyz-spaces-python/blob/master/docs/notebooks/building_numbers.ipynb>`__, demonstrating how to use a spatial search on a big public dataset, loaded from the HERE `Data Hub <https://here.xyz/>`__.

.. image:: https://github.com/heremaps/xyz-spaces-python/raw/master/images/building_numbers.gif


Interactive examples
--------------------

These are some preliminary code snippets that can be executed online. Click on the "Start" button first before you execute the following cells!

.. thebe-button:: Start

.. comment

The following is a cell. Click the "run" button or press Shift-Enter inside the cell to execute it. Launching the computation backend may take a few seconds, and you may need to re-start it.

.. code-block:: python
   :class: thebe

   import xyzspaces
   xyzspaces.__version__

This is another cell. Replace the "MY_XYZ_TOKEN" with your real XYZ token and click "run"  again to search for the GeoJSON feature of the White House in Washington, DC, USA!

.. code-block:: python
   :class: thebe

   import os
   import geojson
   from xyzspaces.datasets import get_microsoft_buildings_space

   os.environ["XYZ_TOKEN"] = "MY_XYZ_TOKEN"
   space = get_microsoft_buildings_space()
   feat = next(space.search(tags=["postalcode@20500"]))
   print(geojson.dumps(feat, indent=4))

More to come... please stay tuned!

