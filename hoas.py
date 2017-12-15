import re
import json
import time

import datetime

from enum import Enum

from bs4 import BeautifulSoup as bs

import getpass
import yaml
import requests

import hoasparser
from utils import print_raw as pr

class AuthException(Exception):
    pass

class HoasInterface:
    BASE_URL = "https://booking.hoas.fi"
    def __init__(self, login_params):
        self.login_params = login_params
        self.session = requests.Session()
        self._login()

    def _login(self):
        """Create session for handling stuff"""
        
        page = self.session.post(f"{self.BASE_URL}/auth/login",
                                 data=self.login_params)
                                 
        # Hoas site redirects user back to login site if auth fails
        if page.url == f"{self.BASE_URL}/auth/login":
            raise AuthException("Login failed")

    def view_page(self, service: int=None, date: datetime.datetime = None):
        try:
            date = f"{date:%d/%m/%y}"
        except Exception:
            date = f"{datetime.datetime.today():%d/%m/%y}"
            
        if service is None:
            service = 363 
        
        page = self.session.get(f"{self.BASE_URL}/varaus/service/timetable/"
                                f"{service}/{date}")
                                
        if page.url == f"{self.BASE_URL}/auth/login":
            self._login()
            page = self.get_hoas_page(service, date)
        page.encoding = "utf-8"
        return page
        
    def reserve(self, service, date):
        pass
        
    def cancel_by_id(self, id):
        pass

    def cancel_by_datetime(self, service, datetime_):
        """ gets calendar from parser by date and checks the time on it, if there 
        is reservation, get id and cancel with it"""
        pass

def load_config():
    config = None
    try:
        with open("config.yaml") as conf:
            config = yaml.load(conf)
    except Exception:
        pass
    return config

def create_config(hoas):
    d = datetime.datetime.today() + datetime.timedelta(days=3)
    with open("dummy.html", "r") as f:
        page = f.read()
   # page = hoas.view_page(date=d).text
    
    soup = bs(page, "html.parser")
    for i in (hoasparser.get_reservation_ids(soup)).items():
        print(i)
    
    
def main(config):
    hoas = HoasInterface(config["login_params"])
    # alex = HoasInterface({"user":"alex", "pass": "asdf"})
    d = datetime.datetime.today() + datetime.timedelta(days=3)
    # page = hoas.view_page(date=d).text
    with open("dummy.html", "r") as f:
        # f.write(page)
        page = f.read()
    soup = bs(page, "html.parser")

        
    print(hoasparser.get_users_reservations(soup))
    create_config(hoas)
if __name__ == "__main__":
    config = load_config()
    main(config)
