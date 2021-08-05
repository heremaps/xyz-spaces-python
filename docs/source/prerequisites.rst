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

* To interact with Interactive Map Layers you will need an account on the HERE Platform. To get more details on the HERE Platform account please check our documentation `Get a HERE account <https://developer.here.com/documentation/identity-access-management/dev_guide/topics/obtain-user-credentials.html>`_.

Once you have the account follow the below steps to get credentials:

*  Go to `HERE Platform Applications and Keys <https://platform.here.com/profile/apps-and-keys>`_ and register a new app.

*  Create a key for the app and download the generated ``credentials.properties`` file.

The HERE platform generated app credentials should look similar to the example below::

   here.user.id = <example_here>
   here.client.id = <example_here>
   here.access.key.id = <example_here>
   here.access.key.secret = <example_here>
   here.token.endpoint.url = <example_here>

You can provide your credentials using any of the following methods:

* Default credentials

* Environment variables

* Credentials file

Default credentials
~~~~~~~~~~~~~~~~~~~~~~
* Place the credentials file into:

  For Linux/MacOS::

   $HOME/.here/credentials.properties

  For Windows::

   %USERPROFILE%\.here\credentials.properties

code snippet to initantiate LS object::

   # credentials will be picked up from credentials.properties file placed at default location.
   from here_location_services import LS

   ls = LS()

Environment Variables
~~~~~~~~~~~~~~~~~~~~~~
You can override default credentials by assigning values to the following environment variables::

   HERE_USER_ID
   HERE_CLIENT_ID
   HERE_ACCESS_KEY_ID
   HERE_ACCESS_KEY_SECRET
   HERE_TOKEN_ENDPOINT_URL

code snippet to initantiate LS object::

   from here_location_services import LS
   from here_location_services.platform.credentials import PlatformCredentials


   credentials = PlatformCredentials.from_env()

   ls = LS(platfrom_credentials=credentials)

Credentials File
~~~~~~~~~~~~~~~~
You can specify any credentials file as an alternative to that found in `~/.here/credentials.properties`. An error is generated if there is no file present at the path, or if the file is not properly formatted.
code snippet to initantiate LS object::

   from here_location_services import LS
   from here_location_services.platform.credentials import PlatformCredentials


   credentials = PlatformCredentials.from_credentials_file("<Path to file>")

   ls = LS(platfrom_credentials=credentials)


