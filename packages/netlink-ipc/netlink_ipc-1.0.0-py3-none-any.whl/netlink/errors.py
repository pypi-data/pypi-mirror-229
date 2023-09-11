class NetLinkException(Exception):
    """
    Base exception for NetLink related errors.
    """
    pass

class UnableToConnect(NetLinkException):
    """
    Raised when the client encounters an issue when connecting to the server.
    """
    def __init__(self, host: str, port: int):
        super().__init__(f"Unable to connect to server at '{host}:{port}'")

class RouteError(NetLinkException):
    """
    Raised when the server encounters an error with a route.
    """
    def __init__(self, route: str, error: Exception):
        super().__init__(f"An error occured in route '{route}': {str(error)}")

class RouteNotFound(NetLinkException):
    """
    Raised when trying to access a route that doesn't exist.
    """
    def __init__(self, route: str):
        super().__init__(f"Unable to find route '{route}'")

class InvalidKey(NetLinkException):
    """
    Raised when an invalid secret_key is used.
    """
    def __init__(self, route: str):
        super().__init__(f"Authorization failed for route '{route}'")

class RouteAlreadyExists(NetLinkException):
    """
    Raised when trying to create a route with the same name an another.
    """
    def __init__(self, route: str):
        super().__init__(f"Route '{route}' already exists.")