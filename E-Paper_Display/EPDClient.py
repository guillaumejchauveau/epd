import socket
import EPDExceptions


class EPDClientConnectionException(Exception):
    pass


class EPDClient:
    def __init__(self):
        """
        Creates an EPDClient. The EPD client will communicate with the EPD service trought the socket.
        """
        self.__socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__connected = False

    @property
    def connected(self) -> bool:
        """
        Getter for the connection's state. This property is kinda artificial as it is set only on connect/disconnect calls or if a timeout is caught, it do not rely on an actual connection information.

        :rtype bool
        """
        return self.__connected

    def connect(self):
        """
        Etablishes a connection with the EPD service.
        """
        self.__socket.connect('/var/run/epd.sock')
        self.__connected = True

    def disconnect(self):
        """
        Closes the connection.
        """
        self.__socket.close()
        self.__connected = False

    def __send(self, data: bytes) -> bytes:
        """
        Sends data throught the socket and waits for a response.

        :param data: The data to send.
        :type data: bytes
        :return The data received.
        :rtype bytes
        :raise EPDClientConnectionException: Raised if the client is not connected.
        :raise OSError: Raised if an error occured during transmittion.
        """
        if not self.connected:
            raise EPDClientConnectionException('Client not connected')

        try:
            self.__socket.send(data)
            return self.__socket.recv(1)
        except OSError as exception:
            self.__connected = False

            raise exception

    def init(self):
        """
        Sends the init command to the service.

        :raise Exception: The exception is raised if an error code is returned.
        """
        result = self.__send(b'0')

        if result != b'0':
            raise Exception

    def update(self):
        """
        Sends the update command to the service.

        :raise EPDExceptions.InvalidFrameException: Raised if an error occurs during frame processing.
        :raise EPDExceptions.InvalidDisplayStatusException: Raised if the display is sleeping.
        :raise Exception: The exception is raised if an unhandled error code is returned.
        """
        result = self.__send(b'1')

        if result == b'2':
            raise EPDExceptions.InvalidFrameException
        elif result == b'3':
            raise EPDExceptions.InvalidDisplayStatusException
        elif result != b'0':
            raise Exception

    def sleep(self):
        """
        Sends the sleep command to the service.

        :raise Exception: The exception is raised if an error code is returned.
        """
        result = self.__send(b'2')

        if result != b'0':
            raise Exception
