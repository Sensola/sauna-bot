import re
import json
import time
import sys

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
        self.cache = {}
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

    def view_page(self, service: int=None, date:
                  datetime.datetime = None, cache_time=20):
        try:
            date = f"{date:%d/%m/%y}"
        except Exception:
            date = f"{datetime.datetime.today():%d/%m/%y}"

        if service is None:
            service = 363

        cache_key = frozenset((service, date))
        new_request_time = time.time() - cache_time
        if (cache_key in self.cache and
                self.cache[cache_key][0] >= new_request_time):
            print("return from cache", self.cache[cache_key][0],
                  cache_time, new_request_time)
            return self.cache[cache_key][1]

        page = self.session.get(f"{self.BASE_URL}/varaus/service/timetable/"
                                f"{service}/{date}")

        if page.url == f"{self.BASE_URL}/auth/login":
            self._login()
            page = self.get_hoas_page(service, date)
        page.encoding = "utf-8"

        self.cache[cache_key] = (time.time(), page)
        return page

    def reserve(self, service, date):
        pass

    def cancel_by_id(self, id):
        pass

    def cancel_by_datetime(self, service, datetime_):
        """ gets calendar from parser by date and checks the time on it, if there
        is reservation, get id and cancel with it"""
        pass


def create_config(hoas):
    d = datetime.datetime.today() + datetime.timedelta(days=3)
    with open("dummy.html", "r") as f:
        page = f.read()
    # page = hoas.view_page(date=d).text

    soup = bs(page, "html.parser")
    for i in (hoasparser.get_reservation_ids(soup)).items():
        print(i)


class Hoas:
    def __init__(self, config={}):
        self.config = config or self.load_config()
        try:
            self.accounts = [HoasInterface(account)
                             for account in self.config["accounts"]]
        except Exception:
            # Todo: Use logger
            print("Couldn't parse configs", file=sys.stderr)
            raise

    def load_config(self):
        config = None
        try:
            with open("config.yaml") as conf:
                config = yaml.load(conf)
        except Exception:
            # Todo: Use logger
            print("Couldn't load configs", file=sys.stderr)
            raise
        print(config)
        return config

    def get_timetables(self, service: int=None,
                       date: datetime=None, cache_time=10):

        state = ("Vapaa", "Varattu", "Varaus")
        for account in self.accounts:
            page = account.view_page(date=date).text
            soup = bs(page, "html.parser")
            topics, cal, left = hoasparser.parse_calendar(soup)
            width = max(*map(len, topics), *map(len, state))

            msg = ((f"{{:{width}}}"*len(topics)).format(*topics)) + "\n"
            for row in cal:
                time, *items = row
                print(row)
                msg += (f"{{:{width}}}" * len(row)).format(
                        time, *(state[r[0]] for r in items)) + "\n"
            msg += left
        return msg

    def get_reservations(self):
        return NotImplemented

    def reserve():
        return NotImplemented


def main(config):
    a = Hoas()
    print(a.get_timetables())


if __name__ == "__main__":
    # config = load_config()
    main(config={})
