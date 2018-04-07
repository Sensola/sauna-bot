import re

from dbhelper import DBHelper


class UserConfigs:
    def __init__(self):
        self.db = DBHelper()

    def handle(self, chat_id, configs):
        if configs == ():  # Just /config returns your configs.
            uconfigs = self.send_configs(chat_id)
            msg = f"Your current configs: \n{uconfigs}"
            return msg
        conf_dict = {}
        for conf in configs:  # We should check both the format and that the keys and values are valid
            check = re.compile("(?P<key>\w*)=(?P<value>\w*)")  # Check if the format is right (key1=value1 key2=value2).
            match = check.match(conf)
            if not match:  # Return error for invalid syntax
                msg = f"Invalid config syntax. \n{configs}"
                return msg
            conf_key = match.group("key")  # The syntax is right, add to dict.
            conf_value = match.group("value")
            conf_dict[conf_key] = conf_value
        # All configs passed the syntax test and are in a dict.
        self.update(chat_id, conf_dict)
        msg = f"Received configs: {conf_dict} raw={configs}"
        return msg

    def __getitem__(self, chat_id):
        row = self.db[chat_id]
        return row

    def update(self, user, conf_dict):
        for key in conf_dict:
            value = conf_dict[key]
            self.db.update_item(user, key, value)

    def add_user(self, chat_id):
        self.db.add_user(chat_id)

    def send_configs(self, chat_id):
        configs = UserConfigs()[chat_id].data
        print(configs)
        uconfigs = ""
        for key in configs:
            value = configs[key]
            uconfigs += f"{key}={value}\n"
        return uconfigs
