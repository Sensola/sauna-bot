import re

from dbhelper import DBHelper


class UserConfigs:
    def __init__(self):
        self.valid_conf_values = {
            "lang": r"fi|en",
            "onreserve": r"true|false",
            "notify": r"^(?:\d|[01]\d|2[0-3]):[0-5]\d|off$",
        }

    def __getitem__(self, chat_id):
        row = DBHelper()[chat_id]
        return row

    def update(self, user, conf_dict):
        for key in conf_dict:
            value = conf_dict[key]
            try:
                DBHelper().update_item(user, key, value)
            except Exception as e:
                msg = "Error occured, try again"
                return msg
        msg = "Configs updated: \n"
        for key in conf_dict:
            value = conf_dict[key]
            msg += f"{key}={value}\n"
        return msg

    def add_user(self, chat_id):
        return DBHelper().add_user(chat_id)

    def check_conf(self, conf):
        check = re.compile(r"^(?P<key>\w*)=(?P<value>[\w:]*)$")  # Check syntax
        match = check.match(conf)
        if not match:
            raise ValueError("Invalid syntax")
        conf_key = match.group("key")
        conf_value = match.group("value")
        if conf_key in self.valid_conf_values.keys():  # Check key
            check = re.compile(self.valid_conf_values[conf_key])  # Check value
            match = check.match(conf_value)
            if not match:
                raise ValueError("Invalid value")
            else:
                return conf_key, conf_value
        else:
            raise ValueError("Invalid key")

    def send_configs(self, chat_id):
        configs = DBHelper()[chat_id].data
        uconfigs = ""
        for key in configs:
            value = configs[key]
            uconfigs += f"{key}={value}\n"
        return f"Your current configs: \n{uconfigs}"
