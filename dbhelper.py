import sqlite3


class DBHelper:
    def __init__(self, dbname="configs.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.columns = ("user", "lang", "onreserve", "notify")

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS configs "\
               "(user UNIQUE, lang, onreserve, notify)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, chat_id):
        stmt = "INSERT INTO configs (user, lang, onreserve, notify) VALUES " \
               "(?, ?, ?, ?)"
        args = (chat_id, "en", "false", "false")  # Default configs for new user
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update(self, user, key, value):
        pass
        # stmt = "UPDATE configs SET (?) = (?) WHERE"

    def __getitem__(self, user):
        stmt = "SELECT * FROM configs WHERE user = (?)"
        args = (user, )
        row = self.conn.execute(stmt, args).fetchone()
        return row[1:]
