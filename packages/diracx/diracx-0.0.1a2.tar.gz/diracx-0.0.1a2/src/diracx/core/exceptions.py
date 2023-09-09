from fastapi import status


class DiracHttpResponse(RuntimeError):
    def __init__(self, status_code: int, data):
        self.status_code = status_code
        self.data = data


class DiracError(RuntimeError):
    http_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str = "Unknown"):
        self.detail = detail


class AuthorizationError(DiracError):
    ...


class PendingAuthorizationError(AuthorizationError):
    """Used to signal the device flow the authentication is still ongoing"""


class ExpiredFlowError(AuthorizationError):
    """Used only for the Device Flow when the polling is expired"""


class ConfigurationError(DiracError):
    """Used whenever we encounter a problem with the configuration"""


class BadConfigurationVersion(ConfigurationError):
    """The requested version is not known"""


class InvalidQueryError(DiracError):
    """It was not possible to build a valid database query from the given input"""
