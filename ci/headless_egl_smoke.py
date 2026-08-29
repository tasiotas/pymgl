"""Minimal Linux wheel smoke test for surfaceless EGL rendering."""

import os

os.environ.pop("DISPLAY", None)
os.environ["EGL_PLATFORM"] = "surfaceless"

import pymgl
from pymgl import Map


style = '{"version":8,"sources":{},"layers":[]}'
width = 32
height = 24
image = Map(style, width=width, height=height).renderBuffer()
expected = width * height * 4

print(f"pymgl_version={pymgl.__version__}")
print(f"DISPLAY={os.environ.get('DISPLAY')!r}")
print(f"EGL_PLATFORM={os.environ['EGL_PLATFORM']}")
print(f"rendered_bytes={len(image)} expected={expected}")
assert len(image) == expected
print("headless_egl_smoke=PASS")
