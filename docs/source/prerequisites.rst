Prerequisites
=============

Before you install the ``xyzspaces`` package make sure you meet the following prerequisites:

Data Hub
--------
* A Python installation, 3.7+ recommended, with the ``pip`` or ``conda`` command available to install dependencies.
* A HERE developer account, free and available under `HERE Developer Portal`_.
* An XYZ API access token from your XYZ Hub server or the `XYZ portal`_ (see also its `Getting Started`_ section) in an environment variable named XYZ_TOKEN which you can set like this (with a valid value, of course)::

   export XYZ_TOKEN=MY-XYZ-TOKEN


.. _HERE Developer Portal: https://developer.here.com/
.. _XYZ portal: https://www.here.xyz/
.. _Getting Started: https://www.here.xyz/getting-started/

Interactive Map Layer
---------------------
* A Python installation, 3.7+ recommended, with the ``pip`` or ``conda`` command available to install dependencies.
* HERE platform paid account, for more information about platform account please check `this <https://developer.here.com/documentation/identity-access-management/dev_guide/topics/obtain-user-credentials.html>`_.
* Once you have the account follow the below steps to get credentials:
    - Go to [HERE Platform Applications and Keys](https://platform.here.com/profile/apps-and-keys) and register a new app.
    - Create a key for the app and download the generated `credentials.properties` file.
    - Place the credentials file into:

    For Linux/MacOS: $HOME/.here/credentials.properties

    For Windows: %USERPROFILE%\.here\credentials.properties

