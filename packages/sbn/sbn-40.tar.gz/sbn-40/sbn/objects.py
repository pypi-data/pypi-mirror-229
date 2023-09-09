# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0902,R0903,E0402,C0411


"a clean namespace"


import datetime
import json
import os
import pathlib
import uuid
import _thread


from json import JSONDecoder, JSONEncoder


def __dir__():
    return (
            'Default',
            'Object',
            'construct',
            'ident',
            'items',
            'keys',
            'kind',
            'read',
            'search',
            'update',
            'values',
            'write',
            'doskip',
            'spl'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()
hooklock = _thread.allocate_lock()
jsonlock = _thread.allocate_lock()


class Object:

    __slots__ = ("__dict__", "__oid__")

    def __init__(self):
        self.__oid__ = ident(self)

    def __contains__(self, key):
        return key in self.__dict__

    def __delitem__(self, key):
        return self.__dict__.__delitem__(key)

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def __str__(self):
        return str(self.__dict__)


class Default(Object):

    __default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return Default.__default__


"methods"


def cls(obj):
    return kind(obj).split(".")[-1]


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, list):
            update(obj, dict(val))
        elif isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def ident(obj) -> str:
    return os.path.join(
                        kind(obj),
                        str(uuid.uuid4().hex),
                        os.path.join(*str(datetime.datetime.now()).split())
                       )


def items(obj) -> []:
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    if isinstance(obj, type({})):
        return obj.keys()
    return obj.__dict__.keys()


def kind(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def search(obj, selector) -> bool:
    res = False
    for key, value in items(selector):
        try:
            val = obj[key]
            if str(value) in str(val):
                res = True
                break
        except KeyError:
            continue
    return res


def update(obj, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        obj[key] = value


def values(obj) -> []:
    return obj.__dict__.values()


"decoder"


class ObjectDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        with jsonlock:
            val = JSONDecoder.decode(self, s)
            if not val:
                val = {}
            return hook(val)

    def raw_decode(self, s, idx=0):
        ""
        return JSONDecoder.raw_decode(self, s, idx)


def hook(objdict) -> type:
    with hooklock:
        obj = Object()
        construct(obj, objdict)
        return obj


def load(fpt, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.load(fpt, *args, **kw)


def loads(string, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)


"encoder"


class ObjectEncoder(JSONEncoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        ""
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(
                      o,
                      (
                       type(str),
                       type(True),
                       type(False),
                       type(int),
                       type(float)
                      )
                     ):
            return o
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            return object.__repr__(o)

    def encode(self, o) -> str:
        ""
        return JSONEncoder.encode(self, o)

    def iterencode(
                   self,
                   o,
                   _one_shot=False
                  ) -> str:
        ""
        return JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)


"utility"


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


def doskip(txt, skipping) -> bool:
    for skp in spl(skipping):
        if skp in txt:
            return True
    return False


def spl(txt) -> []:
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def strip(path) -> str:
    return os.sep.join(path.split(os.sep)[-4:])


"storage"


def read(obj, pth) -> str:
    with disklock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(obj, data)
        obj.__oid__ = strip(pth)
        return obj.__oid__


def write(obj, pth=None) -> str:
    with disklock:
        if not pth:
            try:
                pth = obj.__oid__
            except (AttributeError, TypeError):
                pth = ident(obj)
        cdir(pth)
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(obj, ofile)
        return os.sep.join(pth.split(os.sep)[-4:])
