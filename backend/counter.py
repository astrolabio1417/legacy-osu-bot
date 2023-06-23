import threading, time
from dataclasses import dataclass
from typing import Callable


@dataclass
class Counter:
    count = 0
    run_thread: threading.Thread | None = None
    on_finished: Callable[[], bool] | None = None
    on_count: Callable[[int], int] | None = None
    is_running: bool = False

    def reset(self) -> None:
        # print("counter is reset!")
        self.count = 0
        self.run_thread = None

    def run(self, count: int = 3) -> None:
        self.count = count

        while self.count and self.is_running:
            # print(f"Starting in {self.count} sec...", self.run_thread)

            if self.on_count:
                self.on_count(self.count)

            time.sleep(1)
            self.count -= 1

        if not self.is_running:
            # print("the timer has been killed!")
            return

        # print("count finished")

        if self.on_finished:
            self.on_finished()

        return

    def stop(self) -> None:
        print("thread killed ", self.run_thread)
        self.is_running = False

    def start(self, count: int) -> None:
        if self.run_thread:
            self.stop()
            self.run_thread.join()

        self.is_running = True
        self.run_thread = threading.Thread(target=self.run, args=(count,))
        self.run_thread.start()

    def test(self) -> None:
        count = 0

        while 1:
            time.sleep(1)
            if count in [0, 5, 6]:
                self.start(5)
            count += 1


if __name__ == "__main__":
    t = Counter()

    try:
        t.test()
    except KeyboardInterrupt:
        t.stop()
