import hoas
import time
import logging
import asyncio
import telepot
import telepot.aio
import telepot.exception
from telepot.aio.loop import MessageLoop
from pprint import pprint
from uuid import uuid4


class SensolaBot(telepot.aio.Bot):
    def __init__(self, token, cmds):
        super().__init__(token)
        self.cmds = cmds

    @staticmethod
    def generate_uuid():
        return uuid4()

    @staticmethod
    def register_keyboard(sauna_id):
        return {"inline_keyboard":
                    [[{"text": "yes",
                       "callback_data": sauna_id + "yes"}, ],
                     [{"text": "maybe",
                       "callback_data": sauna_id + "maybe"}, ],
                     [{"text": "no",
                       "callback_data": sauna_id + "no"}, ]
                    ]
        }

    @asyncio.coroutine
    def send_message(self, chat_id, content, reply_markup=None,  parse_mode="HTML",
                     disable_notification=True, disable_web_page_preview=True):
        logging.info(f"Sending message:{chat_id, content}")
        yield from self.sendMessage(
            chat_id, content, parse_mode=parse_mode, reply_markup=reply_markup,
            disable_notification=disable_notification,
            disable_web_page_preview=disable_web_page_preview)

    @asyncio.coroutine
    def handle(self, msg):
        flavor, details = telepot.flance(msg)
        # TODO: log?
        if flavor == "chat" and details[0] == "text":
            logging.info(f"Received message: {msg['text']}")
            content_type, chat_type, chat_id = details
            cmd, *cmd_args = msg['text'].split(" ")
            func = self.cmds.get(cmd, None)
            if not func:
                return
            tuuba = self._loop.run_in_executor(None, func, chat_id)
            asdf = asyncio.wait_for(tuuba, None)
            msg = yield from asdf
            if msg:
                yield from self.send_message(chat_id, msg)

            # yield from self.cmds[cmd](
            #    self, type=chat_type, id=chat_id, cmd=cmd, args=cmd_args)
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
        chat_id, args = kwargs["id"], kwargs["args"]
        if len(args) > 0:
            print(f"[send table of {args[0]} to:]", chat_id)
        else:
            print("[send table of today to:]", chat_id)

    @asyncio.coroutine
    def sauna(self, **kwargs):
        chat_id = kwargs["id"]
        saunas, common_saunas, laundry = hoas.find_users_reservations()  # TODO
        print("[send saunas to:]", chat_id)
        pprint(saunas)
