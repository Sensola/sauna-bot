import logging
import asyncio
import argparse
from contextlib import suppress
from os import path
from functools import wraps

from telepot.aio.loop import MessageLoop
import yaml

import tg
import hoas
from userconfigs import UserConfigs
from dbhelper import DBHelper
from utils import Commands, next_weekday


class SaunaBotCommands(Commands):
    @wraps(Commands.help)
    def help(self, chat_id, cmd="", *, fail=""):
        return super().help(cmd, fail=fail)

    def start(self, chat_id, *args, **kwargs):
        msg = ""
        msg += f"{UserConfigs().add_user(chat_id)}\n\n"
        msg += f"{self.help(chat_id)}"
        return msg

    def tt(self, chat_id, weekday=0, sauna="", *args, **kwargs):
        """Return timetable for a :day: :sauna
day is either in ('mon', 'tue' ...) or ('ma', 'ti' ...)
or weekdays number. 
Sauna is M, H OR E"""

        sauna_id = {"e": 362,
                    "h": 363,
                    "m": 364}.get(sauna.lower(), 363)
        date = None
        with suppress(ImportError):  # ValueError, TypeError):
            date = next_weekday(weekday)
            return '\n'.join((date.strftime("%a %d.%m"), 
                         hoas_api.get_timetables(service=sauna_id, date=date)))
        return ("Didn't understand weekday \n " +
                "Here's the timetable for today\n" +
                hoas_api.get_timetables())

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
    
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    token = config["token"]

    commands = SaunaBotCommands("/")
    bot = tg.SensolaBot(token, commands)
    task = loop.create_task(MessageLoop(
        bot, handle=bot.handle).run_forever())
    print("Listening ...")    
    loop.run_forever()
