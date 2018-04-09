import logging
import asyncio
import telepot
import telepot.aio
import telepot.exception


class SensolaBot(telepot.aio.Bot):
    def __init__(self, token, cmds):
        super().__init__(token)
        self.cmds = cmds

    @asyncio.coroutine
    def send_message(self, chat_id, content, reply_markup=None,
                     parse_mode="HTML", disable_notification=True,
                     disable_web_page_preview=True):
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
            if not cmd.startswith("/"):
                logging.info("No predicate. Ignoring.")
                return
            func = self.cmds[cmd]
            if not func:
                logging.info("Not a valid command.")
                return
            tuuba = self._loop.run_in_executor(None, func, chat_id, *cmd_args)
            asdf = asyncio.wait_for(tuuba, None)
            msg = yield from asdf
            if not msg:
                msg = "202 no content"
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
