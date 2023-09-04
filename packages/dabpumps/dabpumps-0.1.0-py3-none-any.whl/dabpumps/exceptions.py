"""Exceptions used in dabpumps."""


class DConnectError(Exception):
    """General DConnect error occurred."""


class CannotConnectError(DConnectError):
    """Error to indicate we cannot connect."""


class WrongCredentialError(DConnectError):
    """Error to indicate wrong email or password."""


class ForbiddenError(DConnectError):
    """Error to indicate invalid access token."""
