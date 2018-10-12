import pytest
import asyncio
from .. import notifier as notifier

from .utils import CallRecorder


DEFAULT = object()


@pytest.mark.asyncio
async def test_poller_yield():
    items = [1, 2, 3, 4]
    poller = notifier.poller(iter(items).__next__, sleep=0)
    results = []
    async for x in poller:
        results.append(x)
        if x == items[-1]:
            break
    assert results == items


@pytest.mark.asyncio
async def test_poller_delay():
    sleep = 1
    rec = CallRecorder()
    poller = notifier.poller(rec, sleep=sleep, limit=3)
    async for item in poller:
        pass

    it = iter(rec.call_history)
    prev = next(it)
    for item in it:
        assert item.time - prev.time >= sleep
        prev = item
