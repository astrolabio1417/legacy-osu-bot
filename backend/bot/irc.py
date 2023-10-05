import socket
import threading
import time
import queue
from dataclasses import dataclass, field
from typing import Generator
from my_logger import logger
from bot.enums import MESSAGE_YIELD


@dataclass
class OsuIrc:
    username: str
    password: str
    host: str = "irc.ppy.sh"
    port: int = 6667
    irc_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_running: bool = False
    is_connected: bool = False
    send_cooldown_per_second = 0.6  #! 10 message per 5 seconds

    message_queue: queue.Queue[str] = field(default_factory=queue.Queue)
    sender_thread: threading.Thread | None = None

    def connect(self, timeout: float = 10.0) -> bool:
        logger.info(f"~ Connecting to {self.host}:{self.port}...")
        self.is_connected = False

        if not self.username or not self.password:
            logger.info("~ Connection refused! no username or password supplied")
            time.sleep(1)
            return self.is_connected

        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_socket.settimeout(timeout)

        try:
            self.irc_socket.connect((self.host, self.port))
            logger.info("~ Connected!")
            self.is_connected = True
            self.direct_send(f"PASS {self.password}")
            self.direct_send(f"NICK {self.username}")
        except TimeoutError:
            logger.info("~ Timeout Error!")
        except (socket.gaierror, ConnectionRefusedError):
            logger.info("~ No Internet Connection!")

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
            if not self.message_queue.empty() and self.is_connected:
                message = self.message_queue.get()
                self.direct_send(message)
                time.sleep(self.send_cooldown_per_second)

    def direct_send(self, message: str) -> None:
        logger.debug(f"SEND: {message}")
        self.irc_socket.send(f"{message}\n".encode())

    def send(self, message: str) -> bool:
        self.message_queue.put(message)
        return self.is_connected

    def send_private_message(self, channel: str, message: str) -> bool:
        return self.send(f"PRIVMSG {channel} : {message}")

    def message_generator(self) -> Generator[str | MESSAGE_YIELD, None, None]:
        """generate live user messages"""

        buffer: str = ""

        while self.is_running:
            if not self.is_connected:
                reconnected: bool = self.connect()

                if reconnected:
                    yield MESSAGE_YIELD.RECONNECTED
                else:
                    yield MESSAGE_YIELD.RECONECTION_FAILED

                continue

            try:
                message: str = self.receive()
            except Exception:
                logger.info(f"~ Connection has been lost. Receive error")
                self.disconnect()
                yield MESSAGE_YIELD.DISCONNECT
                continue

            if message:
                messages: list[str] = f"{buffer}{message}".split("\n")
                buffer = messages[-1]

                yield from messages[0:-1]
                continue

            yield MESSAGE_YIELD.DISCONNECT
            self.disconnect()
            logger.info("~ Connection has been lost. 0 byte message")

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
