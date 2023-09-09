"""
Custom RPL exceptions.

"""

class RPLException(Exception):
    """Generic RPL exception."""


class RPLServerException(Exception):
    """The server denied your request."""


class RPLInvalidRequestException(Exception):
    """Invalid request to the RPL server exception."""


class RPLUserCredentialsDeniedException(Exception):
    """Invalid user credentials given to server."""