# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0912,R0915,W0105,E0402,R0903


"output cache"


import queue
import textwrap
import threading


from .objects import Object


class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = True
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


class Output:


    def __init__(self):
        self.cache = Object()
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def dosay(self, channel, txt):
        raise NotImplementedError

    def extend(self, channel, txtlist):
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        cache = getattr(self.cache, channel, None)
        cache.extend(txtlist)

    def gettxt(self, channel):
        txt = None
        try:
            cache = getattr(self.cache, channel, None)
            txt = cache.pop(0)
        except (KeyError, IndexError):
            pass
        return txt

    def oput(self, channel, txt):
        if channel is None or txt is None:
            return
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        self.oqueue.put_nowait((channel, txt))

    def out(self):
        while not self.dostop.is_set():
            (channel, txt) = self.oqueue.get()
            if channel is None and txt is None:
                break
            if self.dostop.is_set():
                break
            wrapper = TextWrap()
            try:
                txtlist = wrapper.wrap(txt)
            except AttributeError:
                continue
            if len(txtlist) > 3:
                self.extend(channel, txtlist)
                length = len(txtlist)
                self.dosay(
                           channel,
                           f"use !mre to show more (+{length})"
                          )
                continue
            _nr = -1
            for txt in txtlist:
                _nr += 1
                self.dosay(channel, txt)

    def size(self, chan):
        if chan in self.cache:
            return len(getattr(self.cache, chan, []))
        return 0
