import yaml
from typing import List, Dict
import re
from reservation import SaunaId


def load_config():
    config = {}
    try:
        with open("config.yaml") as conf:
            config = yaml.load(conf)
    except Exception as e:
        print("Could not read 'config.yaml'")
    return config


def get_sauna_ids(sauna_configs) -> Dict[str, SaunaId]:
    sauna_ids = {}
    for sauna in sauna_configs["saunavuorot"]:
        check = re.compile("^Sauna \d, (?P<letter>[A-Z])-talo$")
        match = check.match(sauna)
        assert match, "Invalid page from HOAS system"
        letter = match.group("letter").lower()
        reserve_id = sauna_configs["saunavuorot"][sauna]["reserve"][sauna]
        view_id = sauna_configs["saunavuorot"][sauna]["view"]
        sauna_ids[letter] = SaunaId(view_id, reserve_id)
    return sauna_ids
