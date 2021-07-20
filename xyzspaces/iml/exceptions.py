"""This module defines all the exceptions."""


class AuthenticationException(Exception):
    """
    This ``AuthenticationException`` is raised either authentication
    or authorization on the platform fails.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self) -> str:
        """
        Return the message to be raised for this exception.

        :return: error message
        """
        return """An error occurred during authentication or authorization with HERE
                    platform: Status {status} -
                    Reason {reason}\n Response: {body}""".format(
            status=self.resp.status_code,
            reason=self.resp.reason,
            body=self.resp.text,
        )


class TooManyRequestsException(Exception):
    """Exception raised for API HTTP response status code 429.

    This is a dedicated exception to be used with the `backoff` package, because
    it requires a specific exception class.
    The exception value will be the response object returned by :mod:`requests`
    which provides access to all its attributes, eg. :attr:`status_code`,
    :attr:`reason` and :attr:`text`, etc.
    """

    def __init__(self, resp):
        """
        Instantiate AuthenticationException .
        :param resp: response detail will be stored in this param
        """

        self.resp = resp

    def __str__(self):
        """Return a string from the HTTP response causing the exception.

        The string simply lists the response status code, reason and text
        content, separated with commas.
        """

        return "TooManyRequestsException: Status \
                {status} - Reason {reason}\n\n" "Response: {body}".format(
            status=self.resp.status_code,
            reason=self.resp.reason,
            body=self.resp.text,
        )


class ConfigException(Exception):
    """
    This ``ConfigException`` is raised whenever there is any error related to
    platform configuration.
    """
