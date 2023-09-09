# This file is placed in the Public Domain.
#
# pylint: disable=C0115


from .runtime import wrap, main


def wrapped():
    wrap(main)


if __name__ == "__main__":
    wrapped()
