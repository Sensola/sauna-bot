import asyncio

import pytest

from ..stream_utils import poller, filter_repeating, StreamDivider
from .utils import it2async, yield_tester


@pytest.mark.asyncio
async def test_filter_repeating():
    asd = it2async([1, 1, 2, 2, 2, 3, 3])
    result = [x async for x in filter_repeating(asd)]
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_splitter(event_loop):
    loop = event_loop
    splitter = StreamDivider(it2async([1, 2, 3, 4]))

    source_1 = splitter.wait_for_updates()
    source_2 = splitter.wait_for_updates()
    results = []

    task1 = yield_tester(source_1, [1, 2, 3, 4], results)
    task2 = yield_tester(source_2, [1, 2, 3, 4], results)
    loop.create_task(splitter.run())
    assert all(
        x == [1, 2, 3, 4] for x in (await asyncio.gather(task1, task2, loop=loop))
    )
