Tests
=====

xyzspaces uses `pytest <https://docs.pytest.org/en/stable/>`__ for testing.

You can run the test suite locally::

    pip install -r requirements_dev.txt
    pytest -v --cov=xyzspaces tests

The test suite provides test coverage of around 98% (but less if the tests cannot find your credentials).
