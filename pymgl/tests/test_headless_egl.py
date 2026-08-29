import os

from pymgl import Map


def test_render_buffer_without_x11():
    """Render through surfaceless EGL with no X11 display available."""
    os.environ.pop("DISPLAY", None)
    os.environ["EGL_PLATFORM"] = "surfaceless"

    style = '{"version":8,"sources":{},"layers":[]}'
    width = 32
    height = 24
    image = Map(style, width=width, height=height).renderBuffer()

    assert len(image) == width * height * 4
