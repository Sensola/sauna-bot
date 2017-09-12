import time
import logging
import asyncio
import telepot, telepot.aio, telepot.exception
from telepot.aio.loop import MessageLoop
from pprint import pprint
from uuid import uuid4

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s",
                    datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

TOKEN = "380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k"


class Switch(dict):
    def __missing__(self, key):
        return self.get("default") or (lambda x: None)


class SensolaBot(telepot.aio.Bot):
    def __init__(self, token, cmds):
        super().__init__(token)
        self.cmds = cmds

    @staticmethod
    def generate_uuid():
        return uuid4()

    @staticmethod
    def register_keyboard(sauna_id):
        return {"inline_keyboard": [[{"text": "yes",
                                      "callback_data": sauna_id + "yes"}, ],
                                    [{"text": "maybe",
                                      "callback_data": sauna_id + "maybe"}, ],
                                    [{"text": "no",
                                      "callback_data": sauna_id + "no"}, ],
                                    ]}

    @asyncio.coroutine
    def send_message(self, chat_id, content, reply_markup=None,
                     disable_notification=True, disable_web_page_preview=True):
        logging.info(f"Sending message:{chat_id, content}")
        yield from self.sendMessage(
            chat_id, content, parse_mode="HTML", reply_markup=reply_markup,
            disable_notification=disable_notification,
            disable_web_page_preview=disable_web_page_preview)

    @asyncio.coroutine
    def handle(self, msg):
        flavor, details = telepot.flance(msg)
        # TODO: log?
        if flavor == "chat" and details[0] == "text":
            logging.info(f"Received message: {msg['text']}")
            content_type, chat_type, chat_id = details
            yield from self.cmds[msg['text']](
                self, type=chat_type, id=chat_id, text=msg['text'])
        elif flavor == "inline_query":
            query_id, sender_id, query = details
            # Handle inline query
            pass
        elif flavor == "chosen_inline_result":
            result_id, sender_id, query = details
            # Handle chosen inline result
            pass
        elif flavor == "callback_query":
            query_id, sender_id, data = details
            # Handle callback query
            pass

    @asyncio.coroutine
    def test(self, **kwargs):
        chat_type, chat_id, text = kwargs.values()
        print("received message:", chat_type, chat_id, text)

    @asyncio.coroutine
    def show(self, **kwargs):
        chat_id = kwargs["id"]
        print("[send table to:]", chat_id)

    @asyncio.coroutine
    def sauna(self, **kwargs):
        chat_id = kwargs["id"]
        print("[send saunas to:]", chat_id)


commands = Switch({"/show": SensolaBot.show,
                   "/sauna": SensolaBot.sauna,
                   "/test": SensolaBot.test, })

sensola_bot = SensolaBot(TOKEN, commands)

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(
    sensola_bot, handle=sensola_bot.handle).run_forever())

print("Listening ...")

loop.run_forever()
