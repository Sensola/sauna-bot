import time
import asyncio
from collections import namedtuple

import pytest

CallRecord = namedtuple("CallRecord", ("time", "args", "kwargs"))


class CallRecorder:
    def __init__(self):
        self.call_history = []

    def __call__(self, *args, **kwargs):
        self.call_history.append(CallRecord(time.time(), args, kwargs))


class AwaitRecorder:
    def __init__(self):
        self.call_history = []

    async def __call__(self, *args, **kwargs):
        self.call_history.append(CallRecord(time.time(), args, kwargs))


async def yield_tester(source, expected, results):
    result = []
    async for item in source:
        result.append(item)
    return result


async def it2async(it):
    for item in it:
        await asyncio.sleep(0)
        yield item


class YieldPauser:
    def __init__(self, source):
        self.source = source
        self.yield_next = False
        self.done = False

    async def __anext__(self):
        try:
            while not self.yield_next:
                await asyncio.sleep(0)
            self.yield_next = False

            asd = await self.source.__anext__()
            print(asd)
            return asd
        except StopAsyncIteration:
            self.done = True
            raise

    def __aiter__(self):
        return self

    async def next(self):
        if self.done:
            raise Exception("Iterator was exhausted")
        self.yield_next = True
        while self.yield_next:
            await asyncio.sleep(0)


def pause_generator(source):
    return YieldPauser(source)
