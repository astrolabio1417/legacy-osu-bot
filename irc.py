from dataclasses import dataclass
import socket
from typing import Generator
from constants import MESSAGE_YIELD

@dataclass
class OsuIrc:
    username: str
    password: str
    host: str = "irc.ppy.sh"
    port: int = 6667
    irc_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_running: bool = False
    is_connected: bool = False

    def connect(self, timeout: float = 10.0) -> bool:
        print(f"Connecting to {self.host}:{self.port}...")
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_socket.settimeout(timeout)

        try:
            self.irc_socket.connect((self.host, self.port))
            print("Connected!")
            self.is_connected = True
            self.send(f"PASS {self.password}")
            self.send(f"NICK {self.username}")
        except TimeoutError:
            self.is_connected = False
            print("~ Timeout Error!")
        except socket.gaierror:
            self.is_connected = False
            print("~ No Internet Connection!")

        return self.is_connected

    def disconnect(self) -> None:
        self.is_connected = False
        self.irc_socket.close()

    def close(self) -> None:
        self.is_running = False
        self.disconnect()

    def receive(self, size: int = 2048) -> str:
        return self.irc_socket.recv(size).decode()

    def send(self, message: str) -> bool:
        print(f"send: {message}")
        if self.is_connected:
            self.irc_socket.send(f"{message}\n".encode())
        return self.is_connected

    def send_private(self, channel: str, message: str) -> bool:
        return self.send(f"PRIVMSG {channel} : {message}")

    def message_generator(self) -> Generator[str | int, None, bool]:
        """generate live user messages"""
    
        buffer = ""

        while self.is_running:
            if not self.is_connected:
                reconnected = self.connect()
                
                if reconnected:
                    yield MESSAGE_YIELD['RECONNECTED']
                else:
                    yield MESSAGE_YIELD['RECONECTION_FAILED']

                continue
            
            try:
                message = self.receive()
            except Exception:
                print(f"Connection has been lost. Receive error")
                self.disconnect()
                yield MESSAGE_YIELD['DISCONNECTED']
                continue

            if message:
                messages = f"{buffer}{message}".split("\n")
                buffer = messages[-1]

                for _message in messages[0:-1]:
                    yield _message
                
                continue
            
            yield MESSAGE_YIELD['DISCONNECTED']
            self.disconnect()
            print("Connection has been lost. 0 byte message")

        return False

    def start(self) -> None:
        self.is_running = True
        self.connect()

    def stop(self) -> None:
        self.is_running = False
        self.disconnect()
