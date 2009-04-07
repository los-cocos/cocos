

class Plugin(object):

    def __init__(self, editor):
        self.editor = editor


class Mode(object):
    def on_enable(self):
        pass

    def on_disable(self):
        pass


class EventHandler(object):

    def on_key_press(self, k, m):
        pass

    def on_key_release(self, k, m):
        pass

    def on_mouse_motion(self, px, py, dx, dy):
        pass

    def on_mouse_press(self, px, py, button, m):
        pass

    def on_mouse_release(self, x, y, button, m):
        pass

    def on_mouse_drag(self, px, py, dx, dy, button, m):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

class LayerFactory(object):
    def get_new_layer(self):
        pass

    def layer_to_dict(self, layer):
        pass

    def dict_to_layer(self, dict):
        pass

class EditorLayer(object):
    layer_type = "layer_type"

    def childrenAt(self, x, y):
        pass

