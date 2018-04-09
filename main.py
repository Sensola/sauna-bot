import logging
import asyncio
import argparse
import datetime
from contextlib import suppress
from os import path
from functools import wraps
import re

from telepot.aio.loop import MessageLoop
import yaml

import tg
import hoas
from userconfigs import UserConfigs
from dbhelper import DBHelper
from utils import Commands, next_weekday, get_date


class SaunaBotCommands(Commands):
    @wraps(Commands.help)
    def help(self, chat_id, cmd="", *, fail=""):
        return super().help(cmd, fail=fail)

    def start(self, chat_id, *args, **kwargs):
        msg = ""
        msg += f"{UserConfigs().add_user(chat_id)}\n\n"
        msg += f"{self.help(chat_id)}"
        return msg

    def tt(self, chat_id, *args, **kwargs):
            """Return timetable for a :day: :sauna
    day is either in ('mon', 'tue' ...) or ('ma', 'ti' ...)
    or weekdays number.
    Sauna is M, H or E"""

            weekdays = {
                "en": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                "fi": ["ma", "ti", "ke", "to", "pe", "la", "su"]
            }

            date = get_date(0)
            sauna_id = sauna_ids["h"]["view"]

            if len(args) > 2:
                return "Invalid arguments"
            for arg in args:
                arg = arg.lower()
                if arg.isdigit():
                    date = get_date(int(arg))
                elif len(arg) == 1 and arg.isalpha():
                    try:
                        sauna_id = sauna_ids[arg]["view"]
                    except Exception as e:
                        return "Invalid sauna"
                elif arg in weekdays["en"] or arg in weekdays["fi"]:
                    date = get_date(arg)
                else:
                    return "Invalid arguments"

            with suppress(ImportError):  # ValueError, TypeError):
                return '\n'.join((date.strftime("%a %d.%m"),
                                  hoas_api.get_timetables(
                                      service=sauna_id, date=date)))

    def show(self, *args, **kwargs):
        """Return reserved saunas"""
        return hoas_api.get_reservations()

    def config(self, chat_id, *args, **kwargs):
        """User configuration manager.
Arguments as key=value pairs separated by spaces.
No arguments for a list of current configurations."""
        return UserConfigs().handle(chat_id, args)


def load_config():
    config = {}
    try:
        with open("config.yaml") as conf:
            config = yaml.load(conf)
    except Exception as e:
        print("Could not read 'config.yaml'")
    return config


def get_sauna_ids(sauna_configs):
    sauna_ids = {}
    for sauna in sauna_configs["saunavuorot"]:
        check = re.compile("^Sauna \d, (?P<letter>[A-Z])-talo$")
        match = check.match(sauna)
        letter = match.group("letter").lower()
        reserve_id = sauna_configs["saunavuorot"][sauna]["reserve"][sauna]
        view_id = sauna_configs["saunavuorot"][sauna]["view"]
        sauna_ids[letter] = {"view": view_id, "reserve": reserve_id}
    return sauna_ids


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s",
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
                        
    parser = argparse.ArgumentParser(
        description="Telegram bot for reserving saunas and stuff")
    parser.add_argument("--create-config", action="store_true",
                        help="Find view and reservation ids from hoas site. "
                             "Makes multiple requests to site")
    
    args = parser.parse_args()
    config = load_config()
    if not config \
            or config.get("token") is None \
            or config.get('accounts') is None:
        raise SystemExit("You should have 'config.yaml' file to give hoas "
                         "account(s)\nand telegram bot token. "
                         "See config.example.yaml")
        
    hoas_api = hoas.Hoas(config['accounts'])
    DBHelper().setup()
    if args.create_config or not path.exists("sauna_configs.yaml"):
        sauna_configs = hoas_api.create_config()
        with open("sauna_configs.yaml", "w") as f:
            yaml.dump(sauna_configs, f, default_flow_style=False)
        raise SystemExit("Configs created")
    else:
        with open("sauna_configs.yaml", "r") as f:
            sauna_configs = yaml.load(f)
            sauna_ids = get_sauna_ids(sauna_configs)
    
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    token = config["token"]

    commands = SaunaBotCommands("/")
    bot = tg.SensolaBot(token, commands)
    task = loop.create_task(MessageLoop(
        bot, handle=bot.handle).run_forever())
    logging.info("Listening...")
    loop.run_forever()
