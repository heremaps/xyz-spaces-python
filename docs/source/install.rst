Installation
============

xyzspaces depends for its spatial functionality on a large geospatial, open
source stack of libraries (`Geopandas`_, `turfpy`_). See the
:ref:`dependencies` section below for more details. The C depedencies of Geopandas such as (`GEOS`_, `GDAL`_, `PROJ`_)
can sometimes be a challenge to install. Therefore, we advise you
to closely follow the recommendations below to avoid installation problems.

.. _install-conda:

Installing with Anaconda / conda
--------------------------------

To install xyzspaces and all its dependencies, we recommend to use the `conda`_
package manager. This can be obtained by installing the
`Anaconda Distribution`_ (a free Python distribution for data science), or
through `miniconda`_ (minimal distribution only containing Python and the
`conda`_ package manager). See also the `installation docs
<https://conda.io/docs/user-guide/install/download.html>`__ for more information
on how to install Anaconda or miniconda locally.

The advantage of using the `conda`_ package manager is that it provides
pre-built binaries for all the required dependencies of xyzspaces
for all platforms (Windows, Mac, Linux).

To install the latest version of xyzspaces from `conda-forge`_, you can then do::

    conda install -c conda-forge xyzspaces

Creating a new environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating a new environment is not strictly necessary, but given that installing
other geospatial packages from different channels may cause dependency conflicts
(as mentioned in the note above), it can be good practice to install the geospatial
stack in a clean environment starting fresh.

The following commands create a new environment with the name ``xyz_env``,
configures it to install packages always from conda-forge, and installs
xyzspaces in it::

    conda create -n xyz_env
    conda activate xyz_env
    conda config --env --add channels conda-forge
    conda config --env --set channel_priority strict
    conda install python=3 xyzspaces


.. _install-pip:

Installing with pip
-------------------

xyzspaces can also be installed with pip::

    pip install xyzspaces

.. _install-deps:

.. warning::

    When using pip to install xyzspaces, you need to make sure that all dependencies of Geopandas are
    installed correctly.

    - `fiona`_ provides binary wheels with the dependencies included for Mac and Linux,
      but not for Windows.
    - `pyproj`_ and `shapely`_ provide binary wheels with dependencies included
      for Mac, Linux, and Windows.
    - `rtree`_ does not provide wheels.
    - Windows wheels for `shapely`, `fiona`, `pyproj` and `rtree`
      can be found at `Christopher Gohlke's website
      <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.

    So depending on your platform, you might need to compile and install their
    C dependencies manually. We refer to the individual packages for more
    details on installing those.
    Using conda (see above) avoids the need to compile the dependencies yourself.

Installing from source
----------------------

You may install the latest development version by cloning the
`GitHub` repository and using pip to install from the local directory::

    git clone https://github.com/heremaps/xyz-spaces-python.git
    cd xyz-spaces-python
    pip install .

It is also possible to install the latest development version
directly from the GitHub repository with::

    pip install -e git+https://github.com/heremaps/xyz-spaces-python#egg=xyzspaces

For installing xyzspaces from source, the same :ref:`note <install-deps>` on
the need to have all dependencies correctly installed applies.

See the :ref:`section on conda <install-conda>` above for more details on
getting running with Anaconda.

.. _dependencies:

Dependencies
------------

Required dependencies:

- `requirements`_

Dev dependencies:

- `dev requirements`_



.. _PyPI: https://pypi.python.org/pypi/xyzspaces

.. _GitHub: https://github.com/heremaps/xyz-spaces-python

.. _requirements: https://github.com/heremaps/xyz-spaces-python/blob/master/requirements.txt

.. _dev requirements: https://github.com/heremaps/xyz-spaces-python/blob/master/requirements_dev.txt

.. _Geopandas: https://geopandas.org/

.. _turfpy: https://pypi.org/project/turfpy/

.. _shapely: https://shapely.readthedocs.io

.. _fiona: https://fiona.readthedocs.io

.. _pyproj: https://github.com/pyproj4/pyproj

.. _rtree: https://github.com/Toblerity/rtree

.. _conda: https://conda.io/en/latest/

.. _Anaconda distribution: https://www.anaconda.com/distribution/

.. _miniconda: https://docs.conda.io/en/latest/miniconda.html

.. _conda-forge: https://conda-forge.org/

.. _GDAL: https://www.gdal.org/

.. _GEOS: https://geos.osgeo.org

.. _PROJ: https://proj.org/

