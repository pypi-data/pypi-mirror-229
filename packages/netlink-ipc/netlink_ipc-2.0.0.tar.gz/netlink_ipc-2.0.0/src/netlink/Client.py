import socket
import json
import asyncio

from .objects import ServerResponse, StatusCodes
from .errors import (
    UnableToConnect,
    RouteNotFound,
    InvalidKey,

)

class NetLinkClient:
    def __init__(self, host: str, port: int, secret_key: str):
        """
        Initialize the NetLinkClient class.

        Args:
            host (str): The host address of the server.
            port (int): The port number of the server.
            secret_key (str): The secret key for authentication.
        """
        self.host: str = host
        self.port: int = port
        self.secret_key: str = secret_key

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} host='{self.host}' port={self.port}>"

    def request(self, route_name: str, **kwargs) -> ServerResponse:
        """
        Send a request to the server and receive the response.

        Args:
            route_name (str): The name of the route to request.
            **kwargs: Keyword arguments for the route.

        Returns:
            ServerResponse: The response from the server.

        Raises:
            UnableToConnect: If unable to connect to the server.
            InvalidKey: If authorization with the secret_key fails.
            RouteNotFound: If the specified route was not found.
        """
        request = f"{self.secret_key}|{route_name}|{json.dumps(kwargs)}"
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            raise UnableToConnect(self.host, self.port)
        
        client_socket.sendall(request.encode())

        response = client_socket.recv(1024).decode()
        client_socket.close()

        if response:
            try:
                res = ServerResponse(json.loads(response))

                if res.code == 403:
                    raise InvalidKey(route_name)
                
                elif res.code == 404:
                    raise RouteNotFound(route_name)
                
                return res
            
            except json.JSONDecodeError:
                return ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})
            
        else:
            return ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})
        
class NetLinkAsyncClient:
    def __init__(self, host: str, port: int, secret_key: str):
        """
        Initialize the NetLinkClient class.

        Args:
            host (str): The host address of the server.
            port (int): The port number of the server.
            secret_key (str): The secret key for authentication.
        """
        self.host: str = host
        self.port: int = port
        self.secret_key: str = secret_key

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} host='{self.host}' port={self.port}>"

    async def request(self, route_name: str, **kwargs) -> ServerResponse:
        """
        Send a request to the server and receive the response.

        Args:
            route_name (str): The name of the route to request.
            **kwargs: Keyword arguments for the route.

        Returns:
            ServerResponse: The response from the server.

        Raises:
            UnableToConnect: If unable to connect to the server.
            InvalidKey: If authorization with the secret_key fails.
            RouteNotFound: If the specified route was not found.
        """
        request = f"{self.secret_key}|{route_name}|{json.dumps(kwargs)}"

        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)

            writer.write(request.encode())
            await writer.drain()

            response = await reader.read(1024)
            writer.close()

            if response:
                try:
                    res = ServerResponse(json.loads(response.decode()))

                    if res.code == 403:
                        raise InvalidKey(route_name)
                    
                    elif res.code == 404:
                        raise RouteNotFound(route_name)
                    
                    return res
                
                except json.JSONDecodeError:
                    return ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})
                
            else:
                return ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})

        except ConnectionRefusedError:
            raise UnableToConnect(self.host, self.port)