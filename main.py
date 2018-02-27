import tg
import hoas
import logging
import sqlite3
from os import path
from collections import defaultdict
from telepot.aio.loop import MessageLoop
import yaml

from datetime import datetime, timedelta
from functools import partial, wraps
from utils import Commands
import asyncio
from pprint import pprint 

import argparse


class SaunaBotCommands(Commands):
    @wraps(Commands.help)
    def help(self, msg_id, cmd="", *, fail=""):
        return super().help(cmd, fail=fail)

    def tt(self, *args, **kwargs):
        """Return todays timetable"""
        return hoas_api.get_timetables()

    def show(self, *args, **kwargs):
        """Return reserved saunas"""
        return hoas_api.get_reservations()


def load_config():        
    config = {}
    try:
        with open("config.yaml") as conf:
            config = yaml.load(conf)
    except Exception as e:
        print("Could not read 'config.yaml'")
    return config
    
if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s",
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
                        
    parser = argparse.ArgumentParser(description="Telegram bot for reserving saunas and stuff")
    parser.add_argument("--create-config", action="store_true", 
        help="Find view and reservation ids from hoas site. Makes multiple requests to site")
    
    args = parser.parse_args()
    config = load_config()
    if not config or config.get("token") is None or config.get('accounts') is None:
        raise SystemExit("You should have 'config.yaml' file to give hoas account(s)\n"
                         "and telegram bot token. See config.example.yaml")
        
    hoas_api = hoas.Hoas(config['accounts'])
    if args.create_config or not path.exists("sauna_configs.yaml"):
        sauna_configs = hoas_api.create_config()
        with open("sauna_configs.yaml", "w") as f:
            yaml.dump(sauna_configs, f, default_flow_style=False)
        raise SystemExit("Configs created")
    else:
        with open("sauna_configs.yaml", "r") as f:
            sauna_configs = yaml.load(f)
    
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    token = config["token"]

    commands = SaunaBotCommands("/")
    bot = tg.SensolaBot(token, commands )
    task = loop.create_task(MessageLoop(
        bot, handle=bot.handle).run_forever())
    print("Listening ...")    
    loop.run_forever()
