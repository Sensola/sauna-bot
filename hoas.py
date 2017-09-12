import re
import json
import yaml
from datetime import datetime as dt
from enum import Enum
import requests
from bs4 import BeautifulSoup as bs
import getpass

class Laundry(Enum):
    H = 518
    E = 517


class WashingMachine(Enum):
    pass


class Dryer(Enum):
    H = 637
    E = 680


class Sauna(Enum):
    H = 363
    M = 364
    E = 362

class Service_state(Enum):
    free = 0
    reserved = 1
    our = 2

class AuthException(Exception):
    pass
    
BASE_URL = "https://booking.hoas.fi"


def new_login(login_params) -> requests.Session:
    """ """
    s = requests.Session()
    a = s.post(f"{BASE_URL}/auth/login", data=LOGIN_PARAMS)
    if a.url == f"{BASE_URL}/auth/login":
        raise AuthException("Login failed")
    return s

def scrape_services(s):
    """
    Crawl through hoas site and find service codes for viewing and reserving services.
    returns {'laundry': 
                    {'H': {'view': 11, reserve: 12}, 
                     'E': ...
                    }
              'sauna':
                    ...
               ...
            }        
    """
    ## TODO
    pass

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
        
def get_hoas_page(s, service=None, date=None):
    date = date or dt.today()
    service = service or 123
    
    a = s.get(f"{BASE_URL}/varaus/service/timetable/{service}/{date:%d/%m/%y}")
    a.encoding = "utf-8"
    
    return a

def parse_vacant(soup: bs):
    # s is session, item example: Sauna.H, date is datetime object

    vacant = soup.find(class_='calendar').find_all("a")
    results = []
    for shift in vacant:
        data_date = shift['data-date']
        link = shift['href']
        results.append([data_date, link])
        
    return results

        
def get_all_saunas(s, date=None):
    data = {}
    for sauna in Sauna:
        data[sauna.name] = parse_vacant(s, sauna, date)


def parse_common_saunas(r):
    text = r.text

    # replace " {EN DASH} " with dash so that time range will be "%h-%h"
    text = text.replace(" " + chr(0x2013)+" ", "-")

    # Split datetime, location and info
    sauna = [it.strip() for it in text.split("-\n")]

    # Split date and time
    sauna = sauna.pop(0).split(" ") + sauna

    start_time, end_time = sauna[1].split("-")
    return dict(
            weekday=(sauna[0][:-3]),
            where=sauna[2],
            info=sauna[3],
            start_time=start_time,
            end_time=end_time,
            )


def parse_users_reservations(r):
    text = r.text
    # replace " - " for keeping time range together
    text = text.replace(" - ", "-")
    
    # replace Non-Breaking Hyphen with dash
    text = text.replace(chr(0x2011), "-")
                
    # split different parts separated by space and for each item 
    parts = [it.replace(chr(0xa0), " ") for it in text.split(" ")]
    
    start_time, end_time = parts[1].split("-")
  
    if "laundry" in r.get("class") or "washer" in r.get("class"):
        info, where = parts[2].split(" - ")
    else:
        where = parts[2]
        info = ""
    return dict(
            date=parts[0][3:],
            start_time=start_time,
            end_time=end_time,
            where=where,
            info=info
        )


def find_users_reservations(soup: bs) -> dict:
    """Find users reservations"""
    res = soup.find(class_='myReservations').find_all("a")
    common_saunas = []
    saunas = []
    laundry = []
    for r in res:
        link = r.get("href")
        type_ = r.get("class")
        
        text = r.text
        if link:
            # This is user made reservation
            reservation = parse_users_reservations(r)
            # print(type_)
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


def get_timetable(s, service=None, date=None):
    # Return dummy data
    return {17:Service_state.free,
            18:Service_state.reserved,
            19:Service_state.reserved,
            20:Service_state.free,
            21:Service_state.our,
            }
    
    
if __name__ == "__main__":
    with open("config.yaml") as conf:
        config = yaml.load(conf)
    print(config.get("topic"))
    LOGIN_PARAMS = None
    if config:
        LOGIN_PARAMS = config.get("login_params")
        
    if not LOGIN_PARAMS:
        LOGIN_PARAMS = {"login": input("username: "),
                        "password": getpass.getpass("password: ")}

    s = new_login(LOGIN_PARAMS)
    a = get_hoas_page(s)

    soup = bs(a.text, "html.parser")
    for i in find_users_reservations(soup):
        for j in i:
            print(j)
    print(*parse_vacant(soup), sep="\n")
