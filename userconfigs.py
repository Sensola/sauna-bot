import re

from dbhelper import DBHelper

'''
class omadicti:
        def __init__(self, db, data):

        def __setitem__(self, key, value):
            db.update({key: value})
'''


class UserConfigs:
    def __init__(self):
        self.db = DBHelper()

    def handle(self, chat_id, configs):
        if configs == ():  # Just /config returns your configs.
            uconfigs = UserConfigs()[chat_id]
            columns = self.db.columns
            msg = {}
            for i in range(len(uconfigs)):
                msg[columns[i+1]] = uconfigs[i]
            return msg
        conf_dict = {}
        for conf in configs:
            check = re.compile("(?P<key>\w*)=(?P<value>\w*)")  # Check if the format is right (key1=value1 key2=value2).
            match = check.match(conf)
            if not match:  # Return error for invalid syntax
                msg = f"Invalid config syntax. {configs}"
                return msg
            conf_key = match.group("key")  # The syntax is right, add to dict.
            conf_value = match.group("value")
            conf_dict[conf_key] = conf_value
        # All configs passed the syntax test and are in a dict.

        msg = f"Received configs: {conf_dict} raw={configs}"
        return msg

    def __getitem__(self, chat_id):
        configs = self.db[chat_id]
        return configs

    def __setitem__(self, key, value):
        pass

    def add_user(self, chat_id):
        self.db.add_user(chat_id)
