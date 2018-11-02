import asyncio
import logging
import collections
from contextlib import contextmanager
from datetime import datetime

from stream_utils import poller, StreamDivider, filter_repeating

DEFAULT = object()

logger = logging.Logger(__name__)

class Notifier:
    def __init__(self, stream, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()

        self.loop = loop
        self.sd = StreamDivider(stream)
        self.subscriptions = {}
        self.loop.create_task(self.sd.run())

    async def _new_coro(self, coroutine_callback, limit=0):
        logger.debug("Created new instance")
        async for update in self.sd.wait_for_updates(limit):
            logger.debug("Feeding")
            await coroutine_callback(update)

    def subscribe(self, sub_id, coroutine_callback, limit=0):
        """Create new task which awaits new coro from :coroutine_callback: and save those for cancellation"""

        coro = self._new_coro(coroutine_callback, limit)
        task = self.loop.create_task(coro)

        self.subscriptions[sub_id] = task

    def unsubscribe(self, sub_id):
        task = self.subscriptions.get(sub_id, None)
        if not task:
            raise KeyError("No such subscription")

        task.cancel()
        del self.subscriptions[sub_id]
