from __future__ import division, print_function, unicode_literals

mock_level = 1
import pyglet.resource
import pyglet.app
import pyglet.text.formats.html

version = "1.1.4"

def set_pyglet_text():
    class Label(object):
        def __init__(self, *args, **kwargs):
            pass
    pyglet.text.Label = Label

    # for import layer, which imports python_interpreter
    pyglet.text.caret = None
    pyglet.text.document = None
    pyglet.text.layout = None

set_pyglet_text()
