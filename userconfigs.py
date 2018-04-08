import re

from dbhelper import DBHelper


class UserConfigs:
    def __init__(self):
        self.valid_conf_values = {
            "lang": "fi|en",
            "onreserve": "true|false",
            "notify": "^(?:\d|[01]\d|2[0-3]):[0-5]\d$"
        }

    def __getitem__(self, chat_id):
        row = DBHelper()[chat_id]
        return row

    def handle(self, chat_id, configs):
        if configs == ():  # Just /config returns your configs.
            return self.send_configs(chat_id)
        conf_dict = {}
        for conf in configs:  # Check syntax, keys, and values
            try:
                conf_key, conf_value = self.check_conf(conf)
                conf_dict[conf_key] = conf_value
            except Exception as e:
                msg = f"Error: \n{e}"
                return msg
        return self.update(chat_id, conf_dict)

    def update(self, user, conf_dict):
        for key in conf_dict:
            value = conf_dict[key]
            try:
                DBHelper().update_item(user, key, value)
            except Exception as e:
                msg = f"DATABASE ERROR:\n{e}"
                return msg
        msg = "Configs updated: \n"
        for key in conf_dict:
            value = conf_dict[key]
            msg += f"{key}={value}\n"
        return msg

    def add_user(self, chat_id):
        return DBHelper().add_user(chat_id)

    def check_conf(self, conf):
        check = re.compile("^(?P<key>\w*)=(?P<value>[\w:]*)$")  # Check syntax
        match = check.match(conf)
        if not match:
            raise Exception("Invalid syntax")
        conf_key = match.group("key")
        conf_value = match.group("value")
        if conf_key in self.valid_conf_values.keys():  # Check key
            check = re.compile(self.valid_conf_values[conf_key])  # Check value
            match = check.match(conf_value)
            if not match:
                raise Exception("Invalid value")
            else:
                return conf_key, conf_value
        else:
            raise Exception("Invalid key")

    def send_configs(self, chat_id):
        configs = DBHelper()[chat_id].data
        print(configs)
        uconfigs = ""
        for key in configs:
            value = configs[key]
            uconfigs += f"{key}={value}\n"
        return f"Your current configs: \n{uconfigs}"
