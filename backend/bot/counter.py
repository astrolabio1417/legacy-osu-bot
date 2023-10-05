import threading, time
from dataclasses import dataclass
from typing import Callable
import unittest


@dataclass
class Counter:
    count: int = 0
    run_thread: threading.Thread | None = None
    on_finished: Callable[[], None] | None = None
    on_count: Callable[[int], None] | None = None
    is_running: bool = False

    def run(self, count: int = 3) -> None:
        self.count = count

        while self.count and self.is_running:
            if self.on_count:
                self.on_count(self.count)

            time.sleep(1)
            self.count -= 1

        if not self.is_running:
            return

        if self.on_finished:
            self.on_finished()

        return

    def stop(self) -> None:
        self.is_running = False

    def start(self, count: int) -> None:
        if self.run_thread:
            self.stop()
            self.run_thread.join()

        self.is_running = True
        self.run_thread = threading.Thread(target=self.run, args=(count,))
        self.run_thread.start()


class CounterTestCase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_stop(self):
        counter = Counter()
        counter.start(3)
        counter.stop()
        self.assertFalse(counter.is_running)
        self.assertEqual(counter.count, 3)

    def test_start(self):
        counter = Counter()
        counter.start(3)
        self.assertTrue(counter.is_running)
        counter.stop()

    def test_multiple_start(self):
        counter = Counter()
        counter.start(60)
        self.assertEqual(counter.count, 60)
        counter.stop()
        counter.start(40)
        self.assertEqual(counter.count, 40)
        counter.stop()


if __name__ == "__main__":
    unittest.main()
