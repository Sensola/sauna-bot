import time
import re
import yaml
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from enum import Enum
import requests


class Laundry(Enum):
    H = 518
    E = 517


class Dryer(Enum):
    H = 637
    E = 680


class Sauna(Enum):
    H = 363
    M = 364
    E = 362


BASE_URL = "https://booking.hoas.fi"


def get_reservations(s, item, date=None):
    date = date or dt.today()
    
    a = s.get(f"{BASE_URL}/varaus/service/timetable/{item.value}/{date:%d/%m/%y}")
    a.encoding = "utf-8"

    soup = bs(a.text, "html.parser")
    print(soup)

        
def get_all_saunas(s, date=None):
    data = {}
    for sauna in Sauna:
        data[sauna.name] = get_reservations(s, sauna, date)


def main():
    s = requests.Session()
    a = s.post(f"{BASE_URL}/auth/login", data=LOGIN_PARAMS)
    if a.url == f"{BASE_URL}/auth/login":
        raise SystemExit("Login failed")
    a.encoding = "utf-8"

    soup = bs(a.text, "html.parser")
    
    find_users_reservations(soup)


def parse_common_sauna(saunas: ([...], [...])):
    pass


def lmap(*args,  **kwargs):
    return list(map(*args, **kwargs))


def replaced(t, repl, with_ = ""):
    if isinstance(repl, str):
        repl = [repl]
        
    # if isinstance(str, with_):
    #    with_ = lambda x:   x      
    for c in repl:
        t = t.replace(c, with_)
    return t


def find_users_reservations(soup):
    res = soup.find(class_='myReservations').find_all("a")
    common_saunas = []
    other = []
    for r in res:
        link = r.get("href")

        if link:
            # This is user made reservation
            parts = [it.replace(chr(0xa0)," ") for it
                     in r.text.replace(" - ", "-").split(" ")]
            
        else:
            # This is a Common sauna
            parts = [it.strip() for it in r.text.split("-\n")]
        print(parts)


if __name__ == "__main__":
    with open("config.yaml") as c:
        config = yaml.load(c)
    print(config.get("topic"))
    if config:
        LOGIN_PARAMS = config.get("login_params")
        if not LOGIN_PARAMS:
            LOGIN_PARAMS = {"login": input("username: "), "password": input("password: ")}
    main()
