import json
import os
import pathlib

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


def round_down(number: float, precision: int):
    s = str(number)
    if "." not in s:
        return float(number)

    return float(s[: s.find(".") + precision + 1])


def remove_none(dct: dict):
    return {k: v for k, v in dct.items() if v is not None}
