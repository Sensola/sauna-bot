from typing import Any, Optional

import logging
import time
import sys
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup as bs

import hoasparser


class AuthException(Exception):
    """Authentication failed."""


class HoasInterface:
    BASE_URL = "https://booking.hoas.fi"

    def __init__(self, login_params):
        self.cache: Dict[float, str] = {}
        self.login_params = login_params
        self.session = requests.Session()
        self.configs = []
        self._login()

    def _login(self):
        """Create session for handling stuff"""

        page = self.session.post(f"{self.BASE_URL}/auth/login", data=self.login_params)

        # Hoas site redirects user back to login site if auth fails
        if page.url == f"{self.BASE_URL}/auth/login":
            raise AuthException("Login failed")

    def get_page(self, *args: Any, **kwargs: Any):
        r = self.session.get(*args, **kwargs)

        if page.url == f"{self.BASE_URL}/auth/login":
            self._login()
            r = self.get_hoas_page(service, date)

        r.encoding = "utf-8"
        return r

    def view_page(
        self, service: int = 0, date: Optional[datetime] = None, cache_time=20
    ) -> str:

        if date is None:
            date = datetime.today()

        date = f"{date:%d/%m/%y}"

        cache_key = frozenset((service, date))
        new_request_time = time.time() - cache_time
        if cache_key in self.cache and self.cache[cache_key][0] >= new_request_time:
            logging.debug(
                "return from cache",
                self.cache[cache_key][0],
                cache_time,
                new_request_time,
            )
            return self.cache[cache_key][1]

        r = self.get_page(f"{self.BASE_URL}/varaus/service/timetable/{service}/{date}")
        page = r.text

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


class Hoas:
    def __init__(self, config={}):
        self.config = config
        try:
            self.accounts = [HoasInterface(account) for account in self.config]
        except Exception:
            # Todo: Use logger
            print("Couldn't parse configs", file=sys.stderr)
            raise

    def create_config(self):
        # menu navs = asdf
        config = {}
        for hoas in self.accounts:
            # for stuff in
            page = bs(hoas.view_page(0).text, "html.parser")
            menus = hoasparser.parse_menu(page)
            print(menus)
            for i, (service_type, view_id) in enumerate(menus):
                config[service_type] = {}
                page = bs(hoas.view_page(view_id).text, "html.parser")

                view_ids = hoasparser.parse_view_ids(page)
                # The first viewed sites id is found in menus, but not on page
                view_ids[0] = view_ids[0][0], menus[i][1]
                print(view_ids, menus)
                print(service_type)
                services_dict = {}
                for name, view_id in view_ids:
                    services_dict.setdefault(name, {"reserve": {}, "view": view_id})
                    for i in range(15):
                        d = datetime.today() + timedelta(days=i)
                        page = hoas.view_page(view_id, date=d).text

                        soup = bs(page, "html.parser")
                        services_dict[name]["reserve"].update(
                            filter(
                                (lambda x: x[1]),
                                hoasparser.get_reservation_ids(soup).items(),
                            )
                        )
                        print(services_dict)
                        if len(services_dict[name]["reserve"]) and all(
                            services_dict[name]["reserve"].values()
                        ):
                            break
                    config.setdefault(service_type, {})
                    config[service_type] = services_dict

        return config

    def get_timetables(self, service: int = None, date: datetime = None, cache_time=10):

        state = ("Vapaa", "Varattu", "Oma varaus")
        for account in self.accounts:
            page = account.view_page(service=service, date=date).text
            soup = bs(page, "html.parser")
            topics, cal, left = hoasparser.parse_calendar(soup)
            width = max(*map(len, topics), *map(len, state))

            msg = ((f"{{:{width}}}" * len(topics)).format(*topics)) + "\n"
            for row in cal:
                time, *items = row
                msg += (f"{{:{width}}}" * len(row)).format(
                    time, *(state[r[0]] for r in items)
                ) + "\n"
            msg += left
        return msg

    def get_reservations(self):
        sauna_set = set()
        for account in self.accounts:
            page = account.view_page().text
            soup = bs(page, "html.parser")
            (saunas, common_saunas, laundry) = hoasparser.get_users_reservations(soup)
            for sauna in saunas:
                sauna_set.add(sauna)
        msg = "Reservations:\n"
        for sauna in sorted(sauna_set):
            msg += str(sauna) + "\n"
        return msg

    def reserve(self):
        raise NotImplementedError
