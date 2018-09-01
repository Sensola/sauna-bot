from typing import List, Dict

import logging
import asyncio
import argparse
from os import path

from telepot.aio.loop import MessageLoop
import yaml

import tg
import hoas
from .dbhelper import DBHelper
from .saunaconfigs import load_config, get_sauna_ids
from .saunacommands import SaunaBotCommands


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description="Telegram bot for reserving saunas and stuff"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Find view and reservation ids from hoas site. "
        "Makes multiple requests to site",
    )

    args = parser.parse_args()
    config = load_config()
    if not config or config.get("token") is None or config.get("accounts") is None:
        raise SystemExit(
            "You should have 'config.yaml' file to give hoas "
            "account(s)\nand telegram bot token. "
            "See config.example.yaml"
        )

    hoas_api = hoas.Hoas(config["accounts"])
    DBHelper().setup()
    if args.create_config or not path.exists("sauna_configs.yaml"):
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

    token = config["token"]

    commands = SaunaBotCommands("/")
    bot = tg.SensolaBot(token, commands)
    task = loop.create_task(MessageLoop(bot, handle=bot.handle).run_forever())
    logging.info("Listening...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Bye")
