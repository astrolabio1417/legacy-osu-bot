import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Generator

from bot_enums import MESSAGE_YIELD


@dataclass
class OsuIrc:
    username: str
    password: str
    host: str = "irc.ppy.sh"
    port: int = 6667
    irc_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_running: bool = False
    is_connected: bool = False
    last_sent: float = 0.0
    send_cooldown_per_second = 0.6  #! 10 message per 5 seconds

    message_lists: list[str] = field(default_factory=list)
    sender_thread: threading.Thread | None = None

    def connect(self, timeout: float = 10.0) -> bool:
        print(f"~ Connecting to {self.host}:{self.port}...")

        if not self.username or not self.password:
            self.is_connected = False
            print("~ Connection refused! no username or password supplied")
            time.sleep(1)
            return self.is_connected

        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_socket.settimeout(timeout)

        try:
            self.irc_socket.connect((self.host, self.port))
            print("~ Connected!")
            self.is_connected = True
            self.direct_send(f"PASS {self.password}")
            self.direct_send(f"NICK {self.username}")
        except TimeoutError:
            self.is_connected = False
            print("~ Timeout Error!")
        except (socket.gaierror, ConnectionRefusedError):
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

    def run_sender(self) -> None:
        while self.is_running:
            if not self.message_lists or not self.is_connected:
                continue

            message = self.message_lists[0]
            self.message_lists.pop(0)
            self.direct_send(message)

            if self.send_cooldown_per_second < 0.5:
                time.sleep(1)
                print("~ SEND COOLDOWN TO 1 PER SEC")
            else:
                print("~ SEND COOLDOWN PER SEC: ", self.send_cooldown_per_second)
                time.sleep(self.send_cooldown_per_second)

    def direct_send(self, message: str) -> None:
        print(f"send: {message}")
        self.irc_socket.send(f"{message}\n".encode())

    def send(self, message: str) -> bool:
        self.message_lists.append(message)
        return self.is_connected

    def send_private(self, channel: str, message: str) -> bool:
        return self.send(f"PRIVMSG {channel} : {message}")

    def message_generator(self) -> Generator[str | MESSAGE_YIELD, None, bool]:
        """generate live user messages"""

        buffer = ""

        while self.is_running:
            if not self.is_connected:
                reconnected = self.connect()

                if reconnected:
                    yield MESSAGE_YIELD.RECONNECTED
                else:
                    yield MESSAGE_YIELD.RECONECTION_FAILED

                continue

            try:
                message = self.receive()
            except Exception:
                print(f"~ Connection has been lost. Receive error")
                self.disconnect()
                yield MESSAGE_YIELD.DISCONNECT
                continue

            if message:
                messages = f"{buffer}{message}".split("\n")
                buffer = messages[-1]

                for _message in messages[0:-1]:
                    yield _message

                continue

            yield MESSAGE_YIELD.DISCONNECT
            self.disconnect()
            print("~ Connection has been lost. 0 byte message")

        return False

    def start(self) -> None:
        self.is_running = True

        self.sender_thread = threading.Thread(target=self.run_sender, args=())
        self.sender_thread.start()

        self.connect()

    def stop(self) -> None:
        self.is_running = False
        self.disconnect()

        if self.sender_thread:
            self.sender_thread.join()
