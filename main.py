import tg
import hoas
import logging
import sqlite3
from collections import defaultdict
from telepot.aio.loop import MessageLoop

from datetime import datetime, timedelta
from functools import partial, wraps
from utils import Commands
import asyncio


class SaunaBotCommands(Commands):
    @wraps(Commands.help)
    def help(self, msg_id, cmd="", *, fail=""):
        return super().help(cmd, fail=fail)

    def tt(self, *args, **kwargs):
        """Return todays timetable"""
        return hoas_api.get_timetables()

    def show(self, *args, **kwargs):
        """Return todays saunas"""
        return hoas_api.get_reservations()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s",
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    hoas_api = hoas.Hoas()

    Token = "380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k"

    commands = SaunaBotCommands("/")

    bot = tg.SensolaBot(Token, commands )
    task = loop.create_task(MessageLoop(
        bot, handle=bot.handle).run_forever())
    print("Listening ...")    
    loop.run_forever()
