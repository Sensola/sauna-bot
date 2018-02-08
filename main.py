import tg
import hoas
import logging
import sqlite3
from collections import defaultdict
from telepot.aio.loop import MessageLoop

from datetime import datetime, timedelta
from functools import partial
import asyncio


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s",
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
        
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    hoas_api = hoas.Hoas()

        
    Token = "380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k"
    
    
    commands = defaultdict(
        (lambda *args, **kwargs: "command not found"),
        {'/tt': (lambda chat_id: hoas_api.get_timetables()),
         '/show': (lambda chat_id: hoas_api.get_reservations())
        }
    )


    
    bot = tg.SensolaBot(Token, commands )
    task = loop.create_task(MessageLoop(
        bot, handle=bot.handle).run_forever())
    print("Listening ...")    
    loop.run_forever()

    