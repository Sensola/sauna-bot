import re
import json

import yaml
from datetime import datetime as dt
from enum import Enum

import requests
from bs4 import BeautifulSoup as bs


class Laundry(Enum):
    H = 518
    E = 517


class Washing_machine(Enum):
    pass


class Dryer(Enum):
    H = 637
    E = 680


class Sauna(Enum):
    H = 363
    M = 364
    E = 362

BASE_URL = "https://booking.hoas.fi"


def parse_service(service_str):
    what_re = re.compile("""
                         (?P<type>Sauna|Pesula)\s\d,\s(?P<building>[HME])-(talo|rappu)
                         """, re.VERBOSE)
    enums = {"Sauna": Sauna, "Pesula": Laundry, "Kuivausrumpu": Dryer}
    print(ascii(service_str))
    match = what_re.match(service_str)
    
    if match:
        type_, building = match["type"], match["building"]
        return enums[type_][building]


def get_reservations(s, item, date=None):
    date = date or dt.today()
    
    a = s.get(f"{BASE_URL}/varaus/service/timetable/{item.value}/{date:%d/%m/%y}")
    a.encoding = "utf-8"

    soup = bs(a.text, "lxml")
    print(soup)


def get_all_saunas(s, date = None):
    data = {}
    for sauna in Sauna:
        data[sauna.name] = get_reservations(s, sauna, date)


def main():
    s = requests.Session()
    a = s.post(f"{BASE_URL}/auth/login", data=LOGIN_PARAMS)
    if a.url == f"{BASE_URL}/auth/login":
        raise SystemExit("Login failed")
    a.encoding = "utf-8"
    
    soup = bs(a.text, "lxml")
    print("Current reservations")
    for i, s in  enumerate(find_users_reservations(soup)):
        print(("Saunas", "Common saunas",  "Layndry",)[i])
        for l in s:
           print(json.dumps(l, indent=4))
           pass

def parse_common_saunas(r):
    text = r.text

    # replace " {EN DASH} " with dash so that time range will be "%h-%h"
    text = text.replace(" " +chr(0x2013)+" ", "-")

    # Split datetime, location and info
    sauna = [it.strip() for it in text.split("-\n")]

    # Split date and time
    sauna = sauna.pop(0).split(" ") + sauna

    start_time, end_time = sauna[1].split("-")
    return dict(
            weekday = (sauna[0][:-3]),
            where = sauna[2],
            info = sauna[3],
            start_time= start_time,
            end_time=end_time,
            )

def parse_users_reservations(r):
    text = r.text
    # replace " - " for keeping time range together
    text = text.replace(" - ", "-")
    
    # replace Non-Breaking Hyphen with dash
    text = text.replace(chr(0x2011), "-")
                
    # split different parts separated by space and for each item 
    parts = [it.replace(chr(0xa0)," ") for it in text.split(" ")]
    
    start_time, end_time = parts[1].split("-")
  
    if "laundry" in r.get("class") or "washer"  in r.get("class"):
        info, where = parts[2].split(" - ")
    else:
        where = parts[2]
        info = ""
    return  dict(
            date = parts[0][3:],
            start_time= start_time,
            end_time=end_time,
            where = where,
            info = info
        )
    
def find_users_reservations(soup: bs) -> dict:
    """Find users reservations"""
    res = soup.find(class_ = 'myReservations').find_all("a")
    common_saunas = []
    saunas = []
    laundry = []
    for r in res:
        link = r.get("href")
        type_ =  r.get("class")
        
        text = r.text
        if link:
            # This is user made reservation
            reservation = parse_users_reservations(r)
            #print(type_)
            # print(json.dumps(reservation, indent=4))
            if "washer" in type_ or "dryer" in type_:
                laundry.append(reservation)
            if "sauna" in type_:
                saunas.append(reservation)          
        else:
            # This is a Common sauna, it has to be handled bit differently
            common = parse_common_saunas(r)
            common_saunas.append(common)
    return saunas, common_saunas, laundry


if __name__ == "__main__":
    with open("config.yaml") as c:
        config = yaml.load(c)
    print(config.get("topic"))
    if config:
        LOGIN_PARAMS = config.get("login_params")
        if not LOGIN_PARAMS:
               LOGIN_PARAMS = {"login": input("username: "),
                               "password": input("password: ")}
    main()
