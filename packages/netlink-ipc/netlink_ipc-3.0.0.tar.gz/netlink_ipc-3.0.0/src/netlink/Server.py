import json
import socket
import asyncio
from typing import Callable, Optional

from .errors import RouteAlreadyExists
from .objects import Payload, Route, ServerResponse, StatusCodes


class NetLinkServer:
    def __init__(self, host: str, port: int, secret_key: str):
        """
        Initialize the NetLinkServer class.

        Args:
            host (str): The host address of the server.
            port (int): The port number of the server.
            secret_key (str): The secret key for authentication.
        """
        self.host = host
        self.port = port
        self.secret_key = secret_key
        self.routes = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} host='{self.host}' port={self.port} routes={len(self.routes)}>"

    def route(self, name: Optional[str] = None):
        """
        Decorator to add a route to the server.

        Args:
            name (str, optional): The name of the route. If not provided, the function name will be used as the route name.
        """
        def decorator(func: Callable):
            route = Route(name=name or func.__name__, func=func)

            if route.name in [item[1].name for item in self.routes.items()]:
                raise RouteAlreadyExists(route.name)
            
            self.routes[name if name else func.__name__] = route
            return func
        return decorator

    def start(self):
        """
        Start the server and listen for incoming requests.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, _ = server_socket.accept()
                request = client_socket.recv(1024).decode()
                secret_key, route_name, *params = request.split("|")

                if secret_key != self.secret_key:
                    response = ServerResponse({"response": None, "code": str(StatusCodes.FORBIDDEN), "route": route_name})

                else:
                    if route_name in self.routes:
                        try:
                            payload = Payload(json.loads("|".join(params)))
                            response_data = self.routes[route_name].func(payload)
                            response = ServerResponse({"response": response_data, "code": str(StatusCodes.OK), "route": route_name})
                        except Exception as e:
                            print(f"An exception occurred in route '{route_name}': {str(e)}")
                            response = ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})
                    else:
                        response = ServerResponse({"response": None, "code": str(StatusCodes.NOT_FOUND), "route": route_name})

                client_socket.sendall(json.dumps(response.to_dict()).encode())
                client_socket.close()

        except KeyboardInterrupt:
            print("Server stopping..")

            server_socket.close()

class NetLinkAsyncServer:
    def __init__(self, host: str, port: int, secret_key: str):
        """
        Initialize the NetLinkServer class.

        Args:
            host (str): The host address of the server.
            port (int): The port number of the server.
            secret_key (str): The secret key for authentication.
        """
        self.host = host
        self.port = port
        self.secret_key = secret_key
        self.routes = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} host='{self.host}' port={self.port} routes={len(self.routes)}>"

    def route(self, name: Optional[str] = None):
        """
        Decorator to add a route to the server.

        Args:
            name (str, optional): The name of the route. If not provided, the function name will be used as the route name.

        Raises:
            RouteAlreadyExists: If a route with the specified name or function name already exists.
        """
        async def decorator(func: Callable):
            route = Route(name=name or func.__name__, func=func)

            if route.name in [item[1].name for item in self.routes.items()]:
                raise RouteAlreadyExists(route.name)
            
            self.routes[name if name else func.__name__] = route
            return func
        return decorator

    async def start(self):
        """
        Start the server and listen for incoming requests.
        """
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle incoming client requests asynchronously.

        Args:
            reader (asyncio.StreamReader): The StreamReader to read data from the client.
            writer (asyncio.StreamWriter): The StreamWriter to send data back to the client.
        """
        try:
            data = await reader.read(1024)
            request = data.decode()
            secret_key, route_name, *params = request.split("|")

            if secret_key != self.secret_key:
                response = ServerResponse({"response": None, "code": str(StatusCodes.FORBIDDEN), "route": route_name})
            else:
                if route_name in self.routes:
                    try:
                        payload = Payload(json.loads("|".join(params)))
                        response_data = await self.routes[route_name].func(payload)
                        response = ServerResponse({"response": response_data, "code": str(StatusCodes.OK), "route": route_name})
                    except Exception as e:
                        print(f"An exception occurred in route '{route_name}': {str(e)}")
                        response = ServerResponse({"response": None, "code": str(StatusCodes.INTERNAL_ERROR), "route": route_name})
                else:
                    response = ServerResponse({"response": None, "code": str(StatusCodes.NOT_FOUND), "route": route_name})

            writer.write(json.dumps(response.to_dict()).encode())
            await writer.drain()

        except KeyboardInterrupt:
            print("Server stopping..")