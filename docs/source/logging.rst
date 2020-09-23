Logging Configuration
=====================
By default logging is disabled. To enable logging, use below code snippets in your python code to setup logging at DEBUG level:

.. code-block:: python

    import logging
    from xyzspaces import setup_logging

    setup_logging(default_level=logging.DEBUG)

Default logging configuration is defined in a `file <https://github.com/heremaps/xyz-spaces-python/blob/master/xyzspaces/config/logconfig.json>`__.
This ensures that log messages will be written to the file ``xyz.log`` in your current working directory.
Here is an example log file (xyz.log)::

    2020-02-21 17:55:46,132 - apis.py:130 - ERROR - Curl command: curl --request GET https://xyz.api.here.com/hub/spaces/dummy-111 --header "Authorization: Bearer <XYZ_TOKEN>"
    2020-02-21 17:55:46,133 - apis.py:131 - ERROR - Response status code: 404
    2020-02-21 17:55:46,133 - apis.py:132 - ERROR - Response headers: {'Content-Type': 'application/json', 'Content-Length': '150', 'Connection': 'keep-alive', 'Date': 'Fri, 21 Feb 2020 12:25:46 GMT', 'x-amzn-RequestId': '397c8039-79f1-4956-bbe4-46ca78c7ec2d', 'content-encoding': 'gzip', 'Stream-Id': '397c8039-79f1-4956-bbe4-46ca78c7ec2d', 'x-amzn-Remapped-Content-Length': '150', 'x-amzn-Remapped-Connection': 'keep-alive', 'x-amz-apigw-id': 'IPzblGVFjoEF5pg=', 'x-amzn-Remapped-Date': 'Fri, 21 Feb 2020 12:25:46 GMT', 'X-Cache': 'Error from cloudfront', 'Via': '1.1 e25383e25378de918d3b187b3239eb5b.cloudfront.net (CloudFront)', 'X-Amz-Cf-Pop': 'BOM51-C2', 'X-Amz-Cf-Id': 'nZAJUB_FBiHdojziSoG3SBcMdf8rNyHuOMSlJljyxDNlx1I0O3t9YQ=='}
    2020-02-21 17:55:46,134 - apis.py:133 - ERROR - Response text: {"type":"ErrorResponse","error":"Exception","errorMessage":"The requested resource does not exist.","streamId":"397c8039-79f1-4956-bbe4-46ca78c7ec2d"}


To customize the logging configuration, set the variable XYZ_LOG_CONFIG to hold the full path of the logging configuration options file `logging_config.json <https://github.com/heremaps/xyz-spaces-python/blob/master/xyzspaces/config/logconfig.json>`__::

    export XYZ_LOG_CONFIG=~/logging_config.json

