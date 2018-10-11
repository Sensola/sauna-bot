import asyncio
import collections
from contextlib import contextmanager
from datetime import datetime


DEFAULT = object()


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
        # TODO: Somehow get this to remove the deque
        # after not needed

        deque = collections.deque()
        self.subscriptions.append(deque)

        messages_done = 0
        while amount > messages_done or amount == 0:

            try:
                update = deque.popleft()
                yield update
                messages_done += 1
            except IndexError:
                if self.finished:
                    break
            await asyncio.sleep(0)
        self.subscriptions.remove(deque)


async def filter_repeating(iterable, key=(lambda x, y: x == y)):
    previous = object()
    async for item in iterable:
        if key(item, previous):
            continue
        previous = item
        yield item


class Notifier:
    def __init__(self, stream):
        self.loop = asyncio.get_event_loop()
        self.sd = StreamDivider(stream)  # filter_repeating(poller(func))
        self.subscriptions = {}

    def subscribe(sub_id, coroutine_callback, limit=0):
        """Create new task which awaits new coro from :coroutine_callback: and save those for cancellation"""

        async def new_coro():
            with self.sd.subscribe as stream:
                async for update in stream(limit):
                    await coroutine_callback(update)

        coro = new_coro()
        self.subscriptions[sub_id] = coro
        self.loop.create_task(new_coro())

    def cancel(self, sub_id):
        task = self.subscriptions.get(sub_id)
        task.cancel()

        del self.subscriptions[sub_id]
