import time
import logging
import asyncio
import telepot, telepot.aio, telepot.exception
from telepot.aio.loop import MessageLoop
from pprint import pprint
from uuid import uuid4

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

TOKEN = "380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k"


class SensolaBot(telepot.aio.Bot):
    def __init__(self, token):
        super().__init__(token)

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
            content_type, chat_type, chat_id = details
            # Check for commands
            logging.info(f"Got a message: {msg['text']}")
            yield from self.send_message(chat_id, f"Got a chat message:\n{msg['text']}")
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
    def update_reservations(self, reservations):
        # TODO: Get reservations from another module and update a list of active reservations

        # If there's an object in the list with no active reservation, remove
        # If there's an active reservation without object in the list, create

        return []

    @asyncio.coroutine
    def create_reservation(self, reservation_id, inline_id, reservation_location, reservation_time):
        # TODO: Gotta think how to store reservations
        pass

    @asyncio.coroutine
    def set_user_participation(self, reservation_id, user_name, participation):
        details = "GET RESERVATION DETAILS"  # TODO
        # TODO: Check if user is already participating and has the same participation.
        # TODO: If it's the same, ignore; if it's different, change; if doesn't exist, create.
        modified = None  # Created or changed
        if modified:
            pass
        else:
            logging.info("Status not modified")


sensola_bot = SensolaBot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(
    sensola_bot, handle=sensola_bot.handle).run_forever())

print("Listening ...")

loop.run_forever()
