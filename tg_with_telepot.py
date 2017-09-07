import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint

bot = telepot.Bot('380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k')


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])

MessageLoop(bot, handle).run_as_thread()

print("Listening ...")

while 1:
    time.sleep(10)
