import datetime
from functools import partial
class Commands:
    """
    Class for creating command interfaces.
    Used by subclassing Commands and defining functions.
    >> commands = Commands()
    >> commands["help"] is commands.help
    defines function help(cmd="") which returns docstring for function 'cmd' if given or
    helptext that lists defined functions
    """

    def __init__(self, predicate =""):
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
        """Return help on command if command is given, or else, return all commands"""
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
                    return "Help on command '{}':\n {}".format(cmd, " \n".join(item.__doc__.split("\n")))
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
    zipped_chunks = ((uppers[i:i + width], lowers[i:i + width]) for i in range(0, len(uppers), width))
    for t, i in zipped_chunks:
        print(t)
        print(i)
        print("-" * width)
def next_weekday(weekday, week=0, from_ = None):
    """
       next_weekday(6, week
    """
    now = datetime.datetime.now()
    diff = weekday - d.weekday()
    if diff < 0:
        diff = diff +7
    return  now + datetime.timedelta(days=days_ahead)
if __name__ == "__main__":
    print_raw("asd\n\n\u1234saddsadsaddas \u0000ssafaasfasfsa fsa \n\n asdasd dad ss ääåäåölåplq")