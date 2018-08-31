
from utils import Commands
from functools import wraps
from userconfigs import UserConfigs
from dbhelper import DBHelper
class SaunaBotCommands(Commands):
    @wraps(Commands.help)
    def help(self, chat_id, cmd="", *, fail=""):
        return super().help(cmd, fail=fail)

    def start(self, chat_id, *args, **kwargs):
        """Start a chat with the bot.
        Adds the user into the config database and sends a help message."""
        help = self.help(chat_id)
        add_msg = UserConfigs().add_user(chat_id)

        msg = f"{add_msg}\n\n{help}"
        return msg

    def tt(self, chat_id, *args, **kwargs):
        """Return timetable for a :day: :sauna
        Day is either the abbreviation of your locale
        or number of days from now.
        Sauna is M, H or E"""

        lang = UserConfigs()[chat_id]["lang"]
        weekdays = [
            name.lower()
            for name in sorted(Locale(lang).days["format"]["abbreviated"].values())
        ]

        date = get_date(0)
        sauna_id = sauna_ids["h"].view_id

        if len(args) > 2:
            return "Invalid arguments"

        for arg in args:
            arg = arg.lower()
            if arg.isdigit():
                date = get_date(int(arg))
            elif len(arg) == 1 and arg.isalpha():
                try:
                    sauna_id = sauna_ids[arg].view_id
                except KeyError:
                    return "Invalid sauna"

            elif arg in weekdays:
                date = get_date(arg, weekdays)
            else:
                return "Invalid arguments"

        return "\n".join(
            (
                date.strftime("%a %d.%m"),
                hoas_api.get_timetables(service=sauna_id, date=date),
            )
        )

    def show(self, *args, **kwargs):
        """Return reserved saunas"""
        return hoas_api.get_reservations()

    def config(self, chat_id, *args, **kwargs):
        """User configuration manager.
        Arguments as key=value pairs separated by spaces.
        No arguments for a list of current configurations."""

        if args == ():  # Just /config returns your configs.
            return UserConfigs().send_configs(chat_id)

        conf_dict = {}
        for conf in args:  # Check syntax, keys, and values
            try:
                conf_key, conf_value = UserConfigs().check_conf(conf)
                conf_dict[conf_key] = conf_value
            except ValueError as e:
                msg = f"Error: \n{e}"
                return msg

        return UserConfigs().update(chat_id, conf_dict)
