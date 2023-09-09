# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,W0718,E0402,W0201,W0613,E1120,R0902,W0105
# pylint: disable=W0703


"reactor"


import queue
import ssl
import threading


from .threads import launch


def __dir__():
    return (
            'Reactor',
            'dispatch',
           )


class Reactor:

    errors = []
    output = print

    def __init__(self):
        self._cbs = {}
        self._queue = queue.Queue()
        self._stopped = threading.Event()

    @staticmethod
    def callback(func, obj) -> None:
        try:
            func(obj)
        except Exception as exc:
            excp = exc.with_traceback(exc.__traceback__)
            Reactor.errors.append(excp)
            try:
                obj.ready()
            except AttributeError:
                pass

    def handle(self, obj):
        func = self._cbs.get(obj.type, None)
        if func:
            obj._thr = launch(
                              Reactor.callback,
                              func,
                              obj,
                              name=obj.cmd or obj.type
                             )
        return obj

    def loop(self) -> None:
        while not self._stopped.is_set():
            try:
                obj = self.poll()
                if obj is None:
                    self._stopped.set()
                    continue
                self.handle(obj)
            except (ssl.SSLError, EOFError) as ex:
                exc = ex.with_traceback(ex.__traceback__)
                Reactor.errors.append(exc)
                self.stop()
                self.start()

    def poll(self):
        return self._queue.get()

    def put(self, obj) -> None:
        self._queue.put_nowait(obj)

    def register(self, typ, func) -> None:
        self._cbs[typ] = func

    def start(self):
        launch(self.loop)

    def stop(self):
        self._stopped.set()
        self.put(None)
