# sockets.py

import socket
from typing import (
    Optional, Union, Tuple, Dict, Any, Iterable
)
from urllib.parse import urlparse

from socketsio.service import Service
from socketsio.server import Server
from socketsio.protocols import UDP

from dynamic_service.endpoints import (
    BaseEndpoint, encode, valid_endpoints
)

__all__ = [
    "SocketService"
]

Connection = socket.socket
Host = str
Port = Union[str, int]
Address = Tuple[Host, Port]
Endpoints = Dict[str, BaseEndpoint]
EndpointsContainer = Union[
    Iterable[BaseEndpoint],
    Endpoints
]

class SocketService(Service):
    """
    A class to represent a service object.

    The BaseService is the parent class of service class.
    The service class creates a service object to deploy
    functionality of endpoint objects as a REST API, with sockets backend.

    data attributes:

    - endpoints:
        A set of endpoint objects to serve with the api.

    >>> from dynamic_service.endpoints import BaseEndpoint, GET
    >>> from dynamic_service.service.sockets import SocketService
    >>>
    >>> class MyEndpoint(BaseEndpoint):
    >>>     ...
    >>>
    >>>     def endpoint(self, *args: Any, **kwargs: Any) -> Any:
    >>>         ...
    >>>
    >>> endpoint = MyEndpoint(path="/my_endpoint", methods=[GET])
    >>>
    >>> service = SocketService(
    >>>     endpoints=[endpoint]
    >>> )
    >>>
    >>> service.run()
    """

    __slots__ = "endpoints", "server", 'host', 'port'

    def __init__(
            self,
            connection: Optional[Connection] = None, *,
            host: Optional[Host] = None,
            port: Optional[Port] = None,
            endpoints: Optional[EndpointsContainer] = None
    ) -> None:
        """
        Defines the server datasets for clients and client commands.

        :param connection: The connection socket.
        :param host: The ip address of the server.
        :param port: The port for the server connection.
        :param endpoints: The commands to run for specific requests of the clients.
        """

        self.endpoints = self.valid_endpoints(endpoints or {})

        self.server = Server(connection=connection, protocol=UDP())

        self.host = host
        self.port = port

        if None not in (self.host, self.port):
            self.connect()
        # end if

        Service.__init__(self, server=self.server)
    # end __init__

    @staticmethod
    def valid_endpoints(endpoints: Optional[Any] = None) -> Endpoints:
        """
        Process the endpoints' commands to validate and modify it.

        :param endpoints: The endpoints object to check.

        :return: The valid endpoints object.
        """

        return valid_endpoints(endpoints=endpoints)
    # end valid_endpoints

    def connect(
            self,
            host: Optional[Host] = None,
            port: Optional[Port] = None
    ) -> None:
        """
        Connects the server.

        :param host: The host.
        :param port: The port.
        """

        self.server.bind((host or self.host, port or self.port))
    # end connect

    def respond(self, address: Address, connection: Connection) -> None:
        """
        Sets or updates clients data in the clients' container .

        :param address: The ip address and port used for the sockets' connection.
        :param connection: The sockets object used for the connection.
        """

        url = self.server.receive(connection=connection, address=address).decode()

        payload = urlparse(url)

        kwargs = {
            segment[:segment.find("=")]: segment[segment.find("=") + 1:]
            for segment in payload.query.split("&")
        }

        self.server.send(
            data=encode(self.endpoints[payload.path[1:]](**kwargs)).encode(),
            connection=connection, address=address
        )

        connection.close()
    # end respond
# end SocketService