from typing import Any, Optional, List, Tuple, Dict

import logging
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup as bs

from . import hoasparser


logger = logging.Logger(__name__)


class AuthException(Exception):
    """Authentication failed."""


class HoasInterface:
    BASE_URL = "https://booking.hoas.fi"

    def __init__(self, login_params: Dict[str, str]) -> None:
        self.cache: Dict[frozenset, Tuple[float, str]] = {}
        self.login_params: Dict[str, str] = login_params
        self.session: requests.Session = requests.Session()
        self.configs: list = []
        self._login()

    def _login(self) -> None:
        """Create session for handling stuff"""
        logger.info(
            "HoasInterface: Logging in to {}".format(self.login_params["login"])
        )
        result = self.session.get(f"{self.BASE_URL}/auth/login")
        data = self.login_params
        # print(self.session.cookies.get("csrf_cookie_name"))
        # print(hoasparser.parse_csfr_token(bs(result.text, "html.parser")))
        token = self.session.cookies.get("csrf_cookie_name")
        data["csrf_token_name"] = str(token)
        page = self.session.post(f"{self.BASE_URL}/auth/login", data=data)

        # Hoas site redirects user back to login site if auth fails
        if page.url == f"{self.BASE_URL}/auth/login":
            logger.critical(
                "HoasInterface: Logging in to {} failed".format(
                    self.login_params["login"]
                )
            )
            raise AuthException("Login failed")

    def get_page(self, *args: Any, **kwargs: Any) -> requests.Response:
        r = self.session.get(*args, **kwargs)
        logger.debug("HoasInterface: get_page {}".format(args))
        if r.url == f"{self.BASE_URL}/auth/login":
            self._login()
            r = self.session.get(*args, **kwargs)

            assert r.url != f"{self.BASE_URL}/auth/login"
            logger.info("HoasInterface: got page {}".format(r.url))
        r.encoding = "utf-8"
        return r

    def view_page(
        self, service: int = 0, date: Optional[datetime] = None, cache_time=20
    ) -> str:

        if date is None:
            date = datetime.today()

        date_path: str = f"{date:%d/%m/%y}"

        cache_key = frozenset((service, date_path))
        new_request_time = time.time() - cache_time
        if cache_key in self.cache and self.cache[cache_key][0] >= new_request_time:
            logger.debug(
                "return from cache",
                self.cache[cache_key][0],
                cache_time,
                new_request_time,
            )
            return self.cache[cache_key][1]

        r = self.get_page(
            f"{self.BASE_URL}/varaus/service/timetable/{service}/{date_path}"
        )
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
    def __init__(self, accounts: List[Dict[str, str]]) -> None:
        try:
            self.accounts: List[HoasInterface] = [
                HoasInterface(account) for account in accounts
            ]
        except Exception:
            logger.error("Couldn't parse configs")
            raise

    def create_config(self) -> dict:
        # menu navs = asdf
        config: Dict[str, Any] = {}
        for hoas in self.accounts:
            # for stuff in
            page = bs(hoas.view_page(0), "html.parser")
            menus = hoasparser.parse_menu(page)
            for i, (service_type, view_id) in enumerate(menus):
                config[service_type] = {}
                page = bs(hoas.view_page(view_id), "html.parser")

                view_ids = hoasparser.parse_view_ids(page)
                # The first viewed sites id is found in menus, but not on page
                view_ids[0] = view_ids[0][0], menus[i][1]
                services_dict: Dict[str, Dict[str, Any]] = {}
                for name, view_id in view_ids:
                    services_dict.setdefault(name, {"reserve": {}, "view": view_id})
                    for i in range(15):
                        d = datetime.today() + timedelta(days=i)
                        page = hoas.view_page(view_id, date=d)

                        soup = bs(page, "html.parser")
                        services_dict[name]["reserve"].update(
                            filter(
                                (lambda x: x[1]),
                                hoasparser.get_reservation_ids(soup).items(),
                            )
                        )
                        if len(services_dict[name]["reserve"]) and all(
                            services_dict[name]["reserve"].values()
                        ):
                            break
                    config.setdefault(service_type, {})
                    config[service_type] = services_dict

        return config

    def get_timetables(
        self, service: int = 0, date: datetime = None, cache_time=10
    ) -> List[Tuple[Any, Any, Any]]:

        timetables = []
        for account in self.accounts:
            page = account.view_page(service=service, date=date)
            soup = bs(page, "html.parser")
            topics, cal, left = hoasparser.parse_calendar(soup)
            timetables.append((topics, cal, left))
        return timetables

    def get_reservations(self) -> List[Any]:
        sauna_set = set()
        for account in self.accounts:
            page = account.view_page()
            soup = bs(page, "html.parser")
            (saunas, common_saunas, laundry) = hoasparser.get_users_reservations(soup)
            for sauna in saunas:
                sauna_set.add(sauna)
        return sorted(sauna_set)

    def reserve(self):
        raise NotImplementedError()
