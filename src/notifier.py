from datetime import datetime


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


async def poller(func, callback, sleep=10 * 60):
    """ Call :func: every :sleep: seconds and if result is different than 
        previously, call callback with changed items"""
    previous = []
    while True:
        await asyncio.sleep(sleep)  # Sleep 10 mins
        new = func()
        for item in new:
            if item in previous:
                continue
            await asyncio.sleep(0)
            for user in subscriptions:
                id = user["id"]
                time = user.notif_time
                callback(id, time, callback)
                await asyncio.sleep(0)
