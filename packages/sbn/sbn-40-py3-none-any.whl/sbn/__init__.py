# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0611,W0401,W0614,E0402,E0611,E0603
# flake8: ignore=F401


"""OTP-CR-117/19


NAME

    SBN - Skull, Bones and Number (OTP-CR-117/19)


SYNOPSIS


    sbn <cmd> [key=val] 
    sbn <cmd> [key==val]
    sbn [-c] [-d] [-v]


DESCRIPTION


    SBN is a python3 IRC bot is intended to be programmable  in a
    static, only code, no popen, no user imports and no reading modules from
    a directory, way. It can show genocide and suicide stats of king netherlands
    his genocide into a IRC channel, display rss feeds and log simple text
    messages.

    SBN contains correspondence <writings> with the International Criminal Court, 
    asking for arrest of the king of the  netherlands, for the genocide he is
    committing with his new treatement laws. Current status is "no basis to
    proceed" judgement of the prosecutor which requires a basis to prosecute
    <reconsider> to have the king actually arrested.


INSTALL


    $ pipx install sbn


USAGE

    use the following alias for easier typing

    $ alias sbn="python3 -m sbn"


    list of commands

    $ sbn cmd
    cmd,err,flt,sts,thr,upt


    start a console

    $ sbn -c
    >

    start additional modules

    $ sbn mod=<mod1,mod2> -c
    >

    list of modules

    $ sbn mod
    cmd,err,flt,fnd,irc,log,mdl,mod,
    req, rss,slg,sts,tdo,thr,upt,ver

    to start irc, add mod=irc when
    starting

    $ sbn mod=irc -c

    to start rss, also add mod=rss
    when starting

    $ sbn mod=irc,rss -c

    start as daemon

    $ sbn  mod=irc,rss -d
    $ 


CONFIGURATION


    irc

    $ sbn cfg server=<server>
    $ sbn cfg channel=<channel>
    $ sbn cfg nick=<nick>

    sasl

    $ sbn pwd <nsvnick> <nspass>
    $ sbn cfg password=<frompwd>

    rss

    $ sbn rss <url>
    $ sbn dpl <url> <item1,item2>
    $ sbn rem <url>
    $ sbn nme <url< <name>


COMMANDS


    cmd - commands
    cfg - irc configuration
    dlt - remove a user
    dpl - sets display items
    ftc - runs a fetching batch
    fnd - find objects
    flt - instances registered
    log - log some text
    met - add a user
    mre - displays cached output
    nck - changes nick on irc
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    rss - add a feed
    slg - slogan
    thr - show the running threads


SYSTEMD

    [Unit]
    Description=Skull, Bones and Number (OTP-CR-117/19)
    Requires=network.target
    After=network.target

    [Service]
    DynamicUser=True
    Type=fork
    User=bart
    Group=bart
    PIDFile=sbn.pid
    WorkingDirectory=/home/bart/.sbn
    ExecStart=/home/bart/.local/pipx/venvs/sbn/bin/python3 -m sbn  mod=irc,rss,mdl -d
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target


FILES

    ~/.local/pipx/venvs/sbn/


COPYRIGHT

    SBN is placed in the Public Domain.


"""


__author__ = "skullbonesandnumber@gmail.com"


from . import brokers, clients, objects,  reactor, storage, threads


from .brokers import *
from .clients import *
from .objects import *
from .reactor import *
from .storage import *
from .threads import *


def __dir__():
    return (
            'Broker',
            'Client',
            'Default',
            'Event',
            'Object',
            'Reactor',
            'Repeater',
            'Storage',
            'Thread',
            'construct',
            'edit',
            'fetch',
            'find',
            'ident',
            'items',
            'keys',
            'kind',
            'last',
            'parse',
            'prt',
            'read',
            'search',
            'sync',
            'update',
            'values',
            'write'
           )

