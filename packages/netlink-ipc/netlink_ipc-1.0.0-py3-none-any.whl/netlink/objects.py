from typing import Dict, Any, Callable
import enum

class StatusCodes(enum.Enum):
    """Status codes for NetLink"""
    OK = 200
    FORBIDDEN = 403
    NOT_FOUND= 404
    INTERNAL_ERROR = 500
    
    def __str__(self) -> str:
        return str(self.value)

class Route:
    def __init__(self, name: str, func: Callable):
        """
        Initialize a Route object.
        
        Args:
            name (str): The name of the route.
            func (Callable): The function for the route.
        """
        self.name = name
        self.func = func

class Payload:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a Payload object.

        Args:
            data (dict): A dictionary containing payload data.
        """
        if data and isinstance(data, dict):
            for k, v in data.items():
                setattr(self, k, v)

    def __repr__(self) -> str:
        return "<Payload>"

class ServerResponse:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a ServerResponse object.

        Args:
            data (dict): A dictionary containing response data.
        """
        self.data = data
        self.route = data.get("route")
        self.response = data.get("response")
        self.code = int(data.get("code"))


    def __repr__(self) -> str:
        return f"<ServerResponse code={self.code} response={self.response} route='{self.route}'>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ServerResponse object to a dictionary.

        Returns:
            dict: A dictionary representation of the object.
        """
        return self.data
