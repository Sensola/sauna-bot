import datetime
import yaml
import getpass

from functools import partial
from inspect import cleandoc


class Commands:
    """
    Class for creating command interfaces.
    Used by subclassing Commands and defining functions.

    >> commands = Commands()
    >> commands["help"] is commands.help

    defines function help(cmd="") which returns docstring for function 'cmd'
    if given or helptext that lists defined functions
    """

    def __init__(self, predicate=""):
        assert isinstance(predicate, str)
        self.predicate = predicate

    def __getitem__(self, cmd):
        """Return function self.{cmd} if not found, return help function"""
        assert isinstance(cmd, str)
        name = cmd[len(self.predicate) :]
        # Check that command is valid and not private,
        # protected or special method and attribute for it exists
        if (
            cmd.startswith(self.predicate)
            and not cmd.startswith(self.predicate + "_")
            and hasattr(self, name)
        ):
            item = self.__getattribute__(name)
            if callable(item):
                return item
        # If command not found, return help
        return partial(self.help, fail="No such command")

    def help(self, cmd="", *, fail=""):
        """Return help on command,
        if no command given, return all commands"""
        class_dict = dict(type(self).__dict__)
        # Add this function to class, so that when subclassing,
        # help for help is found
        class_dict.update({"help": self.help})
        if cmd.startswith(self.predicate):
            # Strip predicate
            cmd = cmd[len(self.predicate) :]
        # Check that command exists and is not
        # private, protected or special method
        if (not cmd.startswith("_")) and cmd in class_dict.keys():
            item = class_dict[cmd]
            if callable(item):
                if item.__doc__:
                    return "Help on command '{}':\n.   {}".format(
                        cmd, "\n.    ".join(cleandoc(item.__doc__).split("\n"))
                    )
                return "No help on command '{}'".format(cmd)
        # If no cmd given or wrong cmd given, return commands
        commands = []
        for key, value in class_dict.items():
            if not key.startswith("_"):
                if callable(value):
                    commands.append(key)
        msg = (
            "Commands:\n {}".format(", ".join(commands))
            + "\n for more help on command, use "
            + "{}help command".format(self.predicate)
        )
        if fail:
            msg = fail + "\n" + msg
        return msg


class ConfigurationError(Exception):
    pass


def get_date(day, weekdays=[]):
    today = datetime.date.today()
    current_weekday = today.weekday()
    if day in weekdays:
        weekday = weekdays.index(day)
        day = weekday - current_weekday
        if weekday < current_weekday:
            day += 7
    date = today + datetime.timedelta(days=day)
    return date


def get_hoas_credentials():
    positive = ("y", "yes")
    config = {}
    try:
        with open("config.yaml", "r") as f:
            config = yaml.load(f)
    except IOError as e:
        import os
        import sys

        if os.isatty(0):
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            token = input("Telegram token: ")
            config = {
                "accounts": [{"username": username, "password": password}],
                "token": token,
            }
            if input("Save for later use? y/n ") in positive:
                with open("config.yaml", "w") as f:
                    f.write(yaml.dump(config, default_flow_style=False))
            print("You can edit config.yaml to change credentials or add more accounts")
        else:
            raise ConfigurationError(
                "You should create config.yaml to add configs.\n"
                "See config.example.yaml"
            )
    return config
