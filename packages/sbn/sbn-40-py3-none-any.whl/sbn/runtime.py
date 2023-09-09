# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402,W0212,R1710,W0611,E0611,R0903,W0105,C0103


"binary"


import os
import readline
import sys
import termios
import time
import threading
import traceback
import _thread


from sbn import modules


from .clients import Client, Event, command, mods, parse
from .objects import Default, spl
from .reactor import Reactor
from .storage import Storage
from .threads import Thread, launch


Cfg = Default()
Cfg.mod = "bsc,err,flt,mod,sts,thr"
Cfg.name = __file__.split(os.sep)[-2]


class CLI(Client):

    def raw(self, txt):
        print(txt)


class Console(Client):

    prompting = threading.Event()

    def announce(self, txt):
        pass

    def handle(self, obj):
        command(obj)
        obj.wait()

    def prompt(self):
        Console.prompting.set()
        inp = input("> ")
        Console.prompting.clear()
        return inp

    def poll(self):
        try:
            return self.event(self.prompt())
        except EOFError:
            _thread.interrupt_main()

    def raw(self, txt):
        if Console.prompting.is_set():
            txt = "\n" + txt
        print(txt)
        Console.prompting.clear()
        sys.stdout.flush()


"utility"


def cprint(txt):
    if "v" in Cfg.opts:
        print(txt)
        sys.stdout.flush()


def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    os.umask(0)
    with open('/dev/null', 'r', encoding="utf-8") as sis:
        os.dup2(sis.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as sos:
        os.dup2(sos.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())


def scan(pkg, modstr="", initer=False, wait=False) -> []:
    if not pkg:
        return []
    inited = []
    scanned = []
    threads = []
    if modstr == "":
        modstr = mods(pkg.__path__[0])
    for modname in spl(modstr):
        module = getattr(pkg, modname, None)
        if not module:
            continue
        scanned.append(modname)
        Client.scan(module)
        Storage.scan(module)
        if initer:
            try:
                module.init
            except AttributeError:
                continue
            inited.append(modname)
            threads.append(launch(module.init, name=f"init {modname}"))
    if wait:
        for thread in threads:
            thread.join()
    return inited


def wrap(func) -> None:
    if "d" in Cfg.opts:
        Client.debug("terminal disabled")
        return
    old = termios.tcgetattr(sys.stdin.fileno())
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
    for exc in Reactor.errors + Thread.errors:
        traceback.print_exception(
                                  type(exc),
                                  exc,
                                  exc.__traceback__
                                 )

"runtime"


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "a" in Cfg.opts:
        Cfg.mod = ",".join(mods(modules.__path__[0]))
    if "v" in Cfg.opts:
        tme = time.ctime(time.time()).replace("  ", " ")
        Client.output = print
        Client.debug(f"{Cfg.name.upper()} started {tme} {Cfg.opts.upper()}")
    if "d" in Cfg.opts:
        Client.output = None
        daemon()
        scan(modules, Cfg.mod, True)
        while 1:
            time.sleep(1.0)
        return
    csl = Console()
    if "c" in Cfg.opts:
        scan(modules, Cfg.mod, True, True)
        csl.start()
        csl.wait()
    else:
        scan(modules, Cfg.mod)
        cli = CLI()
        evt = Event()
        evt.orig = object.__repr__(cli)
        evt.txt = Cfg.otxt
        command(evt)
        evt.wait()
