from datetime import datetime
import asyncio

class Notifier:
    """Handler for managing callbacks"""

    def __init__(self, loop):
        self.loop = loop
        self.active = {}

    def schedule(self, id, when, callback):
        """Schedule new call to :callback: at :when: and save it under :id:"""
        now = datetime.now().timestamp()
        delay = when.timestamp() - now

        def callback_with_remove():
            callback()
            del self.active[id][when]

        print(f"Delay: {delay}")
        future = self.loop.call_later(delay, callback_with_remove)

        self.active.setdefault(id, {})
        self.active[id].setdefault(when, [])
        self.active[id][when].append(future)

    def view_notifications(id):
        notifs = self.active.get(id)
        return list(notifs) if notifs else {}

    def cancel(id, when):
        for x in self.active.get(id, {}).get(when, ()):
            if x:
                x.cancel()
        try:
            del self.active[id][when]
        except Exception:
            logger.log("")


async def poller(func, args = [], sleep=10 * 60, limit=0, call_limit=0):
    """ Call :func: every :sleep: seconds and if result is different than 
        previously, yield result"""
        
    loop = asyncio.get_event_loop()
    yielded = 0
    calls = 0

    previous = object()
    while True:
        new_result = await loop.run_in_executor(
            None, func, *args, 
        )

        if new_result != previous:
            yield new_result
            yielded += 1

            previous = new_result
        calls += 1

        await asyncio.sleep(sleep)
        if (limit > 0 and yielded > limit) or (call_limit > 0 and calls > call_limit):
            break

