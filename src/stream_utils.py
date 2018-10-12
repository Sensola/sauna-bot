import asyncio
import collections
from contextlib import contextmanager
from datetime import datetime


async def poller(func, args=[], sleep=10 * 60, limit=0):
    """ Call :func: every :sleep: seconds and yield result"""

    loop = asyncio.get_event_loop()
    yielded = 0
    calls = 0

    while True:
        new_result = await loop.run_in_executor(None, func, *args)

        yield new_result
        yielded += 1

        await asyncio.sleep(sleep)
        if limit > 0 and yielded > limit:
            break


class StreamDivider:
    """Helper class for getting updates from one coroutine source to multiple"""

    def __init__(self, stream):
        self.stream = stream
        self.finished = False
        self.subscriptions = []

    async def run(self):
        """Coroutine that feeds results from stream to subscriptions"""
        async for update in self.stream:
            for sub in self.subscriptions:
                sub.append(update)
        self.finished = True

    async def wait_for_updates(self, amount=0):
        """Async iterator for getting updates"""

        deque = collections.deque()
        self.subscriptions.append(deque)

        messages_done = 0
        try:
            while amount > messages_done or amount == 0:
                try:
                    update = deque.popleft()
                    yield update
                    messages_done += 1
                except IndexError:
                    if self.finished:
                        break
                await asyncio.sleep(0)
        finally:
            # Removes the correct deque from the list. Finishes quickly enough.
            # Better way would be to use some other datastructure,
            # subs.remove(deque) just removes first empty deque

            for i, val in enumerate(self.subscriptions):
                if val is deque:
                    self.subscriptions.pop(i)


async def filter_repeating(iterable, key=(lambda x, y: x == y)):
    previous = object()
    async for item in iterable:
        if key(item, previous):
            continue
        previous = item
        yield item
