import json
import operator
import os
import pathlib
import random
from typing import Union

import yaml


def read_json(*path):
    with open(os.path.join(*path)) as f:
        return json.loads(f.read())


def read_yaml(*path):
    with open(os.path.join(*path)) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def read_config(path: str) -> dict:
    extension = pathlib.Path(path).suffix
    if "yaml" in extension:
        return read_yaml(path)
    if "json" in extension:
        return read_json(path)


def round_down(number: Union[float, int, None], precision: int):
    if number is None:
        return

    s = str(number)
    if "." not in s:
        return float(number)

    return float(s[: s.find(".") + precision + 1])


def remove_none(dct: dict):
    return {k: v for k, v in dct.items() if v is not None and v != "None"}


def generate_ascii(start: int, end: int):
    return (chr(n) for n in range(start, end))


def generate_random_string(chars: str, size: int):
    return "".join(random.choice(chars) for _ in range(size))


def get_object_from_module(module_name: str, object_name: str):
    import importlib

    module = importlib.import_module(module_name)

    return getattr(module, object_name)


logical_operators = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
}


def compare(left_value, logical_operator, right_value):
    return logical_operators[logical_operator](left_value, right_value)


def interval_to_seconds(interval: str):

    time = int(interval[0 : len(interval) - 1])
    metric = interval[-1]

    if metric.lower() == "s":
        return time
    elif metric == "m":
        return time * 60
    elif metric.lower() == "h":
        return time * 3600
    elif metric.lower() == "d":
        return time * 86400
    elif metric.lower() == "w":
        return time * 604800
    elif metric == "M":
        return time * 2629800
    elif metric.lower() == "y":
        return time * 31557600
