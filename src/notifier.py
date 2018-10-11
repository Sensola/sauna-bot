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
        
        self.subcriptions = []

    async def run(self):
        """Coroutine that feeds results from coroutine to subscriptions"""
        
        if self.running == True:
            raise Exception("SubManager was running already")
        self.running = True

        while self.running:
            async for update in self.stream:
                for sub in self.subcriptions:
                    sub.append(result)
    
    async def wait_for_updates(self, amount=0):
        """Async iterator for getting updates"""
        # TODO: Somehow get this to remove the deque
        # after not needed

        deque = collections.deque
        self.subscriptions.append(deque)

        messages_done = 0
        while amount > messages_done or amount == 0:
            for update in deque:
                yield update
                messages_done += 1
    

async def main():
    man = SubscriptionManager(
        if_changed(
            poller(hoas.get_reservations())
        )
    )



        
def command(msg_id):
    subscribe(msg_id)
    
async def filter_repeating(iterable, key=(lambda x, y: x ==  y)):
    previous = object()
    async for item in iterable:
        if key(item, previous):
            continue
        previous = item
        yield item


class Notifier:
    def __init__(self, stream):
        self.loop = asyncio.get_event_loop()
        self.sd = StreamDivider(stream) # filter_repeating(poller(func))
        self.subscriptions = {}

    def subscribe(sub_id, coroutine_callback, limit=0):
        """Create new task which awaits new coro from :coroutine_callback: and save those for cancellation"""
        
        async def new_coro():
            async for update in self.sd.wait_for_update(limit):
                await coroutine_function(update)

        coro = new_coro()
        self.subscriptions[sub_id] = coro
        self.loop.create_task(new_coro())
    
    def cancel(self, sub_id):
        task = self.subscriptions.get(sub_id)
        task.cancel()

        del self.subscriptions[sub_id]

