import re
from functools import wraps
import itertools
from utils import print_raw as pr

from bs4 import BeautifulSoup as bs
from collections import OrderedDict


def str_to_soup(f):
    @wraps(f)
    def decorated(arg):
        if isinstance(arg, str):
            arg = bs(arg)
        return f(arg)
    return decorated


def get_users_reservations(soup) -> (dict, dict, dict):
    """Find users reservations from Beautifull soup object"""
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


def parse_common_saunas(r):
    # regs = re.compile(
    r"""
    \s*
    (?P<day>\w*)
    \s
    (?P<start_time>\d{2}:\d{2})
    \s\u2013\s
    #(?P<end_time>\d{2}:\d{2})
    \s*-\n*
    (?P<where>.*)
    \t*-\n
    """  # , re.MULTILINE | re.VERBOSE | re.UNICODE)
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


def get_reservation_ids(soup):

    topics, cal, reservations_left = parse_calendar(soup)
    fin = OrderedDict(
            itertools.islice(zip(topics, itertools.repeat(None)), 1, None))

    if not cal:
        return fin
    # First row is (sub)services' names and second is remaining reservations
    for time, *items in cal:
        # Skip times
        for name, (status, item) in \
                itertools.islice(zip(topics, items), 1, None):

            if status == 1:
                continue
            print(item.get("href"))
            fin[i] = item.get("href")
    return fin


def parse_calendar(soup):
    # TODO: Check that this works also with laundries
    calendar = soup.find(class_='calendar').find_all("tr")
    final_cal = []
    cal = iter(calendar)
    topics = [x.text.strip()for x in next(cal).find_all("td")]
    topics[0] = "time"
    try:
        reservations_left = next(cal).text.strip()
    except StopIteration:
        # There is no data for this day
        reservations_left = ""

    print(topics)
    print(reservations_left)
    for row in cal:
        # print(row)
        data = {}
        time, *data_cols = row.find_all("td")
        # If item inside tag is a link, it's free
        this_row = [time.text]
        for data in data_cols:
            info = {}
            # defafult reserved
            status = 1

            if data.a:
                info = data.a.attrs
                # ´free
                status = 0
                if False:
                    # TODO: handle users reserved
                    status = 2
                    pass
            this_row.append((status, info))
        final_cal.append(this_row)

    return topics, final_cal, reservations_left
