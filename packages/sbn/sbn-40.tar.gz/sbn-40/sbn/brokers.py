# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,W0718,E0402,W0201,W0613,E1120,R0902


"brokering"


class Broker:

    objs = []

    @staticmethod
    def add(obj) -> None:
        Broker.objs.append(obj)

    @staticmethod
    def byorig(orig):
        for obj in Broker.objs:
            if object.__repr__(obj) == orig:
                return obj
        return None

    @staticmethod
    def bytype(typ):
        for obj in Broker.objs:
            if typ in object.__repr__(obj):
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        try:
            Broker.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def show(obj):
        bot = Broker.byorig(obj.orig)
        if bot:
            for txt in obj.result:
                bot.say(obj.channel, txt)
