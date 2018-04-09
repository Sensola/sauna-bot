import datetime
from functools import partial, singledispatch
from contextlib import suppress


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
        name = cmd[len(self.predicate):]
        # Check that command is valid and not private,
        # protected or special method and attribute for it exists
        if (cmd.startswith(self.predicate)
                and not cmd.startswith(self.predicate + "_")
                and hasattr(self, name)):
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
            cmd = cmd[len(self.predicate):]
        # Check that command exists and is not
        # private, protected or special method
        if (not cmd.startswith("_")) and cmd in class_dict.keys():
            item = class_dict[cmd]
            if callable(item):
                if item.__doc__:
                    return "Help on command '{}':\n {}".format(
                        cmd, " \n".join(item.__doc__.split("\n")))
                return "No help on command '{}'".format(cmd)
        # If no cmd given or wrong cmd given, return commands
        commands = []
        for key, value in class_dict.items():
            if not key.startswith("_"):
                if callable(value):
                    commands.append(key)
        msg = ("Commands:\n {}".format(", ".join(commands)) +
               "\n for more help on command, use " +
               "{}help command".format(self.predicate))
        if fail:
            msg = fail + "\n" + msg
        return msg


def print_raw(text, width=50):
    uppers = ""
    lowers = ""
    for t in text:
        a = repr(t)[1:-1]
        b = hex(ord(t))[2:]
        pad = 5
        uppers += a.rjust(pad)
        lowers += b.rjust(pad)
    zipped_chunks = ((uppers[i:i + width], lowers[i:i + width])
                     for i in range(0, len(uppers), width))
    for t, i in zipped_chunks:
        print(t)
        print(i)
        print("-" * width)


def get_date(day):
    weekdays = {
        "en": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "fi": ["ma", "ti", "ke", "to", "pe", "la", "su"]
    }
    today = datetime.date.today()
    current_weekday = today.weekday()
    if day in weekdays["en"]:
        weekday = weekdays["en"].index(day)
        if weekday < current_weekday:
            day = weekdays["en"].index(day) + (7 - current_weekday)
        else:
            day = weekdays["en"].index(day) - current_weekday
    if day in weekdays["fi"]:
        weekday = weekdays["fi"].index(day)
        if weekday < current_weekday:
            day = weekdays["fi"].index(day) + (7 - current_weekday)
        else:
            day = weekdays["fi"].index(day) - current_weekday
    date = today + datetime.timedelta(days=day)
    return date


@singledispatch
def next_weekday(weekday, weeks=0, from_=None):
    raise TypeError(f"Weekday must be string or int, was {weekday:!r}")


@next_weekday.register(int)
def _(weekday, weeks=0, from_=None):
    """
       >> next_weekday(6, week
    """
    now = from_ or datetime.datetime.now()
    diff = weekday - now.weekday()
    if diff < 0:
        diff = diff + 7
    diff = diff + weeks * 7
    return now + datetime.timedelta(days=int(diff))


@next_weekday.register(str)
def _(weekday, weeks=0, from_=None):
    if weekday.isdigit():
        return next_weekday(int(weekday), weeks, from_)
        
    weekday = weekday.lower()
    
    ind = None
    days_en = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    days_fi = ["ma", "ti", "ke", "to", "pe", "la", "su"]
    #  Check if found in known day abbreviations
    for check in (days_en, days_fi):
        with suppress(ValueError):
            ind = check.index(weekday)
            break
    
    if ind is None:
        raise ValueError("Weekday must be 3 letter english or 2 letter "
                         "finnish abbrevation")
    return next_weekday(ind, weeks, from_)

if __name__ == "__main__":
    print(datetime.datetime.today().weekday())
    print(f"{next_weekday('thu',1).strftime('%a %d.%m')}")
    print(f"{next_weekday('2',0).strftime('%a %d.%m')}")
