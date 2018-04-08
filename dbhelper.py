import sqlite3


class DBHelper:
    def __init__(self, dbname="configs.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.columns = ["user", "lang", "onreserve", "notify"]

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS configs "\
               "(user UNIQUE, lang, onreserve, notify)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, chat_id):
        stmt = "INSERT INTO configs (user, lang, onreserve, notify) VALUES " \
               "(?, ?, ?, ?)"
        args = (chat_id, "en", "false", "false")  # Default configs for new user
        try:
            self.conn.execute(stmt, args)
            self.conn.commit()
            return "New user added"
        except:
            return "Database error"

    def update_item(self, user, key, value):
        stmt = "UPDATE configs SET (?) = (?) WHERE user = (?)"
        args = (key, value, user)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def __getitem__(self, user):
        stmt = "SELECT * FROM configs WHERE user = (?)"
        args = (user, )
        row = self.conn.execute(stmt, args).fetchone()
        rowdict = dict(zip(self.columns, row))
        del rowdict["user"]
        return DBRow(user, rowdict, self)


class DBRow:
    def __init__(self, user, data, db):
        self.user = user
        self.data = data
        self.db = db

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.db.update_item(self.user, key, value)
