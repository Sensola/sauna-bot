import asyncio

import pytest
from .. import notifier

from .utils import AwaitRecorder, yield_tester, it2async, pause_generator

@pytest.mark.asyncio
async def test_notifier(event_loop):
    # TODO: Maybe break onto multiple tests
    source = pause_generator(it2async([1,2,3,4]))
    notif = notifier.Notifier(source, loop=event_loop)
    
    aw1 = AwaitRecorder()
    aw2 = AwaitRecorder()
    aw3 = AwaitRecorder()

    notif.subscribe("a", aw1)
    await source.next()
    
    notif.subscribe("b", aw2)
    notif.subscribe("c", aw3)

    await source.next()
    await source.next()
    
    assert list(notif.subscriptions.keys()) == ["a", "b", "c"]

    await asyncio.sleep(0.2) 
    
    notif.unsubscribe("c")

    assert list(notif.subscriptions.keys()) == ["a", "b"]
    
    await source.next()
    await source.next()
    await asyncio.sleep(1) 
    
    assert [x.args[0] for x in aw1.call_history] == [1,2,3,4]
    assert [x.args[0] for x in aw2.call_history] == [2,3,4] 
    assert [x.args[0] for x in aw3.call_history] == [2,3]
