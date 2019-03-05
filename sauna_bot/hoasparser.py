from typing import Tuple

import re
import itertools
import datetime

from collections import OrderedDict, namedtuple


class Reservation(namedtuple("Reservation", "start end where info")):
    def __str__(self):
        return f"{self.start:%a %d.%m.%Y from %H:%M} to {self.end:%H:%M} in {self.where} {self.info}"

def parse_csfr_token(soup):
    for tag in soup.find_all("input"):
        if tag.get("name") == "csrf_token_name":
            return tag.get("value")

def get_users_reservations(soup) -> Tuple[list, list, list]:
    """Find users reservations from Beautiful soup object"""
    res = soup.find(class_="myReservations").find_all("a")
    common_saunas = []
    saunas = []
    laundry = []
    for r in res:
        link = r.get("href")
        type_ = r.get("class")

        if link:
            # This is user made reservation
            reservation = parse_users_reservations(r)
            if "washer" in type_ or "dryer" in type_:
                laundry.append(reservation)
            if "sauna" in type_:
                saunas.append(reservation)
        else:
            # This is a Common sauna, it has to be handled bit differently
            common = parse_common_saunas(r.text)
            common_saunas.append(common)
    return saunas, common_saunas, laundry


def parse_common_saunas(text: str):
    # Normalize time range
    text = text.replace(" \N{EN DASH} ", "-")

    # Split datetime, location and info
    dt_range, location, info = [it.strip() for it in text.split("-\n")]

    # Split date and time
    date, time = dt_range.split(" ")

    start_time, end_time = time.split("-")
    return {
        "weekday": (date[:-3]),
        "where": location,
        "info": info,
        "start_time": start_time,
        "end_time": end_time,
    }


def parse_users_reservations(r):
    text = r.text
    # replace " - " for keeping time range together
    text = text.replace(" - ", "-")

    # replace Non-Breaking Hyphen with dash
    text = text.replace(chr(0x2011), "-")

    # split different parts separated by space and for each item
    parts = [it.replace(chr(0xA0), " ") for it in text.split(" ")]

    start_time, end_time = parts[1].split("-")

    if "laundry" in r.get("class") or "washer" in r.get("class"):
        info, where = parts[2].split(" - ")
    else:
        where = parts[2]
        info = ""
    date = parts[0][3:]
    start = datetime.datetime.strptime(f"{date} {start_time}", "%d.%m.%Y %H:%M")
    end = datetime.datetime.strptime(f"{date} {end_time}", "%d.%m.%Y %H:%M")
    return Reservation(start=start, end=end, where=where, info=info)


def get_reservation_ids(soup):
    topics, cal, reservations_left = parse_calendar(soup)
    fin = OrderedDict(
        itertools.islice(zip(topics, itertools.repeat(OrderedDict())), 1, None)
    )
    url_regexp = re.compile(
        r"https://booking.hoas.fi/varaus/service/reserve/(?P<id>[0-9]*)/.*"
    )
    if not cal:
        return fin
    # First row is (sub)services' names and second is remaining reservations
    for time, *items in cal:
        # Skip times
        for name, stuff in zip(itertools.islice(topics, 1, None), items):
            if stuff[0] == 1:
                continue
            if not fin[name]:
                url = stuff[1].get("href")
                match = url_regexp.match(url)
                if match:
                    id = match.group("id")
                    fin[name] = id
    return fin


def parse_view_ids(soup):
    fin = []
    service_nav = soup.find(class_="service-nav")
    fin.append((service_nav.span.text, None))
    # TODO: do not guess
    for a in service_nav.find_all("a"):
        # Take last part of url
        fin.append((a.text, a["href"].rsplit("/", 1)[-1]))
    return fin


def parse_menu(soup):
    fin = []
    menu = soup.find(class_="menu")
    for a in menu.find_all("a"):
        view_id = a["href"].rsplit("/", 1)[-1]
        if view_id.isnumeric():
            fin.append((a["class"][0], view_id))
    return fin


def parse_calendar(soup):
    # TODO: Check that this works also with laundries
    calendar = soup.find(class_="calendar").find_all("tr")
    final_cal = []
    cal = iter(calendar)
    topics = [x.text.strip() for x in next(cal).find_all("td")]
    topics[0] = "time"
    try:
        reservations_left = next(cal).text.strip()
    except StopIteration:
        # There is no data for this day
        reservations_left = ""

    for row in cal:
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
                if data.a.get("class") == ["myReservation"]:
                    status = 2
            this_row.append((status, info))
        final_cal.append(this_row)
    return topics, final_cal, reservations_left
