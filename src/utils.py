# utils.py
import os
import sys

def resource_path(relative_path: str) -> str:
    """
    PyInstaller + dev friendly resource path resolver.
    Pass paths relative to project root, e.g. "assets/maps/town.json"
    """
    # When running from src/, project root is parent of this file's folder.
    base_dev = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller stores data in _MEIPASS
        base = sys._MEIPASS
    else:
        base = base_dev
    return os.path.join(base, relative_path)


def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )
