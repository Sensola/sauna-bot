import pytest
import asyncio
from .. import notifier as notifier

import time
from collections import namedtuple

CallRecord = namedtuple("CallRecord", ("time", "args", "kwargs"))

DEFAULT = object()


@pytest.mark.asyncio
async def test_poller_yield():
    items = [1,2,3,4]
    poller=notifier.poller(iter(items).__next__, sleep=0)
    results = []
    async for x in poller:
        results.append(x)
        if x == items[-1]:
            break
    assert results == items

class CallRecorder:
    def __init__(self):
        self.call_history=[]
    
    def __call__(self, *args, **kwargs):
        self.call_history.append(CallRecord(time.time(), args, kwargs))
        


@pytest.mark.asyncio
async def test_poller_delay():
    sleep=1
    rec = CallRecorder()
    poller=notifier.poller(rec, sleep=sleep, call_limit=3)
    async for item in poller:
        pass 

    it = iter(rec.call_history)
    prev = next(it)
    for item in it:
        assert item.time - prev.time >= sleep
        prev = item
    

