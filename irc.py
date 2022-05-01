from dataclasses import dataclass
import socket
from typing import Generator


@dataclass
class OsuIrc:
    username: str
    password: str
    __host: str = "irc.ppy.sh"
    __port: int = 6667
    __socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __running: bool = False
    __connected: bool = False

    @property
    def connected(self) -> bool:
        return self.__connected

    def connect(self, timeout: float = 10.0) -> bool:
        print(f"Connecting to {self.__host}:{self.__port}...")
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(timeout)

        try:
            self.__socket.connect((self.__host, self.__port))
            print("Connected!")
            self.__connected = True
            self.send(f"PASS {self.password}")
            self.send(f"NICK {self.username}")
        except TimeoutError:
            print("~ Timeout Error!")
        except socket.gaierror:
            print("~ No Internet Connection!")

        return self.connected

    def disconnect(self) -> None:
        self.__connected = False
        self.__socket.close()

    def close(self) -> None:
        self.__running = False
        self.disconnect()

    def receive(self, size: int = 2048) -> str:
        return self.__socket.recv(size).decode()

    def send(self, message: str) -> bool:
        print(f"send: {message}")
        if self.connected:
            self.__socket.send(f"{message}\n".encode())
        return self.connected

    def send_private(self, channel: str, message: str) -> bool:
        return self.send(f"PRIVMSG {channel} : {message}")

    def message_generator(
        self,
    ) -> Generator[str | int, None, bool]:
        """generate live user messages"""
        buffer = ""

        while self.__running:
            if self.__connected:
                try:
                    message = self.receive()
                except Exception:
                    print(f"Connection has been lost. Receive error")
                    self.disconnect()
                    yield -1
                    continue

                if message:
                    messages = f"{buffer}{message}".split("\n")
                    buffer = messages[-1]

                    for _message in messages[0:-1]:
                        yield _message
                else:
                    yield -1
                    self.disconnect()
                    print("Connection has been lost. 0 byte message")
            else:
                yield -2
                self.connect()

        return False

    def start(self) -> None:
        self.__running = True

    def stop(self) -> None:
        self.__running = False
        self.disconnect()
