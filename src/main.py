"""Sauna-bot.

Telegram bot for reserving saunas and stuff

usage:
  main.py (-h | --help)
  main.py --create-config
  main.py (-d  | --debug ) [<debuglevel>]
  main.py

Options:
  -h, --help       Show this help message and exit
  --create-config  Find view and reservation ids from hoas site. Makes
                   multiple requests to site
"""

import logging
import asyncio
import argparse
from os import path

from telepot.aio.loop import MessageLoop
import yaml
from docopt import docopt

import tg
import hoas
from dbhelper import DBHelper
import utils
from saunaconfigs import load_config, get_sauna_ids
from saunacommands import SaunaBotCommands
from stream_utils import poller, filter_repeating
from templates import format_diff
from notifier import Notifier

def sauna_diff(previous, new):

    reserved = []
    cancelled = []

    for item in previous:
        if item not in new:
            cancelled.append(item)

    for item in new:
        if item not in previous:
            reserved.append(item)
    return reserved, cancelled


async def reservation_changes(stream):
    previous = []
    async for saunas in stream:
        yield format_diff(*sauna_diff(previous, saunas))
        previous = saunas

async def send_to_senso( message):
    await bot.send_message(219882470, message)

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        level=logging.INFO,
    )
    args = docopt(__doc__, version="Sauna-bot 0.0.1")

    config = utils.get_hoas_credentials()

    if not config or config.get("token") is None or config.get("accounts") is None:
        raise SystemExit(
            "You should have 'config.yaml' file to give hoas "
            "account(s)\nand telegram bot token. "
            "See config.example.yaml"
        )

    hoas_api = hoas.Hoas(config["accounts"])
    DBHelper().setup()
    if args.get("--create_config") or not path.exists("sauna_configs.yaml"):
        sauna_configs = hoas_api.create_config()
        with open("sauna_configs.yaml", "w") as f:
            yaml.dump(sauna_configs, f, default_flow_style=False)
        print("Configs created")
        raise SystemExit(0)

    else:
        with open("sauna_configs.yaml", "r") as f:
            sauna_configs = yaml.load(f)
            sauna_ids = get_sauna_ids(sauna_configs)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    sauna_poller = reservation_changes(filter_repeating(poller(hoas_api.get_reservations, sleep=5)))

    notif = Notifier(sauna_poller)
    notif.subscribe("senso", send_to_senso)

    token = config["token"]
    loop.create_task(send_to_senso("Mui.")) 
    commands = SaunaBotCommands(hoas_api, sauna_ids, "/")
    bot = tg.SensolaBot(token, commands)
    task = loop.create_task(MessageLoop(bot, handle=bot.handle).run_forever())
    
    logging.info("Listening...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Bye")
