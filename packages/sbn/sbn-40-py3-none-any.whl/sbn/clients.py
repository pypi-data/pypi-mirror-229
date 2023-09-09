# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,E0402,W0201,W0613,E1120,R0902,W0105,W0612
# pylint: disable=W0718


"clientele"


import inspect
import os
import time
import threading


from .brokers import Broker
from .objects import Default
from .reactor import Reactor


def __dir__():
    return (
            'Client',
            'Event',
            'command',
            'mods',
            'parse'
           )


__all__ = __dir__()


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.result = []
        self.type = "command"

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self):
        Broker.show(self)

    def wait(self) -> []:
        if self._thr:
            self._thr.join()
        self._ready.wait()
        return self.result


class Client(Reactor):

    cmds = {}
    skip = ["PING", "PONG", 'PRIVMSG']

    def __init__(self):
        Reactor.__init__(self)
        Broker.add(self)
        self.register("command", command)

    @staticmethod
    def add(func):
        Client.cmds[func.__name__] = func

    def announce(self, txt):
        self.raw(txt)

    @staticmethod
    def debug(txt):
        donext = False
        for skp in Client.skip:
            if skp in txt:
                donext = True
        if donext:
            return
        Client.output(txt)

    def event(self, txt):
        evt = Event()
        evt.txt = txt
        evt.orig = object.__repr__(self)
        evt.type = "event"
        return evt

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Client.add(cmd)

    def wait(self):
        while not self._stopped.is_set():
            time.sleep(1.0)


"utility"


def command(obj):
    parse(obj, obj.txt)
    obj.type = "command"
    func = Client.cmds.get(obj.cmd, None)
    if func:
        try:
            func(obj)
            Broker.show(obj)
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Client.errors.append(exc)
    obj.ready()


def mods(path):
    res = []
    for fnm in os.listdir(path):
        if fnm.endswith("~"):
            continue
        if not fnm.endswith(".py"):
            continue
        if fnm in ["__main__.py", "__init__.py"]:
            continue
        res.append(fnm[:-3])
    return sorted(res)


def parse(obj, txt=None) -> None:
    args = []
    obj.args = []
    obj.cmd = obj.cmd or ""
    obj.gets = obj.gets or {}
    obj.hasmods = False
    obj.mod = obj.mod or ""
    obj.opts = obj.opts or ""
    obj.sets = obj.sets or {}
    obj.otxt = txt or ""
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            obj.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd
