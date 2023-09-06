import json
import threading
import time
from dataclasses import fields
from distutils.version import StrictVersion
from typing import Optional

import pkg_resources
import requests

from dataclasses import dataclass
from functools import total_ordering

from mstuff.http import http_get

_suppress_version_warning = False


def warn_if_old(mod_name):
    if not _suppress_version_warning:
        # need trailing slash in url below. It should be an automatic redirect, but I was having issues...
        made_it = False

        def debug_timer():
            time.sleep(10)
            if not made_it:
                print("I think pypi might be having that weird issue again!")

        # print(f"about to http_get: https://pypi.org/project/{mod_name}/")
        t = threading.Thread(daemon=True, target=debug_timer)
        t.start()
        resp = http_get(f"https://pypi.org/project/{mod_name}/", status_checker=None)
        made_it = True

        if resp.status_code == 404:
            print(f"package {mod_name} does not yet exist?")
            return
        try:
            this_version = pkg_resources.get_distribution(mod_name).version
        except pkg_resources.DistributionNotFound:
            this_version = None
        # https://stackoverflow.com/a/27239645/6596010
        def versions(package_name):
            url = "https://pypi.org/pypi/%s/json" % (package_name,)
            data = json.loads(requests.get(url).text)
            the_versions = list(data["releases"].keys())
            the_versions.sort(key=StrictVersion)
            return the_versions

        online_versions = versions(mod_name)
        latest_version = online_versions[len(online_versions) - 1]
        if this_version != latest_version:
            print(
                f"WARNING: You are using {mod_name} {this_version} but the latest version is {latest_version}. In the terminal use `python -m pip install {mod_name} --upgrade` to update."
            )


# https://stackoverflow.com/questions/68417319/initialize-python-dataclass-from-dictionary
def class_from_args(cls, d):
    field_set = {f.name for f in fields(cls) if f.init}
    filtered_arg_dict = {k: v for k, v in d.items() if k in field_set}
    return cls(**filtered_arg_dict)


# https://stackoverflow.com/a/1305682/6596010
class Obj(object):
    def __init__(self, d):
        for k, v in d.items():
            if not isinstance(k, str):
                raise Exception(f"keys must be str, not {type(k)}")
            if isinstance(v, (list, tuple)):
                setattr(self, k, [Obj(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, Obj(v) if isinstance(v, dict) else v)

    def __str__(self):
        return f"[Obj with fields: {','.join([f'{k}: {best_short_str(v)}' for k, v in self.__dict__.items()])}]"

    def __repr__(self):
        return str(self)


def best_short_str(o):
    if isinstance(o, int):
        return str(o)
    if isinstance(o, float):
        return str(o)
    if isinstance(o, list):
        return f"list(len={len(o)})"
    if isinstance(o, tuple):
        return f"tuple(len={len(o)})"
    if isinstance(o, dict):
        return f"dict(len={len(o)})"
    if isinstance(o, str):
        l = len(o)
        if l <= 10:
            return f'"{o}"'
        return f"str(len={l})"
    if isinstance(o, bytes):
        l = len(o)
        if l <= 10:
            return f'"{o}"'
        return f"bytes(len={l})"
    if isinstance(o, Obj):
        return f"obj(len={len(o.__dict__)})"
    if isinstance(o, bool):
        return str(bool)
    return str(type(o))


# https://stackoverflow.com/a/6907371/6596010
@dataclass
@total_ordering
class Duration:
    sec: float

    @property
    def ms(self):
        return self.sec * 1000

    def __neg__(self):
        return Duration(-self.sec)

    def __lt__(self, other):
        return self.sec < other.sec


class Stopwatch:
    instances = []

    def __init__(self, name):
        Stopwatch.instances.append(self)
        self.name = name
        self.start = None
        self.stop = None
        self.dur = None

    def tic(self):
        self.start = time.time()

    def __enter__(self):
        self.tic()

    def toc(self):
        self.stop = time.time()
        self.dur = Duration(self.stop - self.start)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.toc()


stopwatch = Stopwatch


class MultiStopwatch:
    def __init__(self):
        self.s: Optional[Stopwatch] = None

    def finish(self):
        if self.s is not None:
            self.s.toc()

    def click(self, name: str):
        self.finish()
        s = Stopwatch(name)
        s.tic()
        self.s = s

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()


def take(itr, n):
    r = []
    for x in itr:
        if n > 0:
            r.append(x)
        else:
            return r
        n -= 1
    return r


def stopwatch_report():
    sorted_stopwatches = sorted(Stopwatch.instances, key=lambda i: -i.dur)
    sorted_stopwatches = take(sorted_stopwatches, 5)
    r = "Highest Duration Stopwatches:"
    for s in sorted_stopwatches:
        r += f"\n\t{s.name:20}\t{s.dur.sec :10.3} sec"
    return r


def error(s):
    raise Exception(s)


def read(file):
    with open(file) as f:
        return f.read()


def load(file):
    with open(file) as f:
        return json.load(f)
