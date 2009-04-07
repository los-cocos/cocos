from pyglet.window import key

from plugin import Plugin, Mode, EventHandler

from plugins.handlers import MouseEventHandler


class CameraMode(Mode, MouseEventHandler):
    name = 'camera'

    def __init__(self, editor):
        self.ed = editor

    def on_enable(self):
        self.ed.register_handler(self)

    def on_disable(self):
        self.ed.unregister_handler(self)

    def on_key_press(self, k, m):
        if k == key.PAGEUP or k == key.PAGEDOWN:
            if k == key.PAGEUP:
                direction = 1
            elif k == key.PAGEDOWN:
                direction = -1

            x, y = self.ed.mouse_position

            self.ed.zoom(x, y, direction)
            return True

    def on_mouse_drag(self, px, py, dx, dy, b, m):
        self.ed.layers.x += dx
        self.ed.layers.y += dy


class CameraPlugin(Plugin):
    name = 'camera'

    def __init__(self, editor):
        self.ed = editor
        self.mode = CameraMode(editor)
        editor.register_mode("sprite", self.mode)
