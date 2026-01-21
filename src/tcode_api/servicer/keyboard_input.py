"""Minimal keyboard reading code from StackOverflow

source: https://stackoverflow.com/a/67939368
"""

import enum
import os
import sys
import termios
import tty

_ord_to_str_map: dict[int, str] = {
    9: "tab",
    10: "return",
    27: "esc",
    32: "space",
    65: "up_arrow",
    66: "down_arrow",
    67: "right_arrow",
    68: "left_arrow",
    127: "backspace",
}


def get_key() -> str:
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
                return _ord_to_str_map.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
