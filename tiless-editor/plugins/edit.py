import pyglet
from pyglet.window import key

from plugin import Plugin, Mode
from plugins.handlers import MouseEventHandler


class EditMode(Mode, MouseEventHandler):
    name = 'edit'

    def __init__(self, editor):
        self.ed = editor
        self.hovering = None
        self.hovered_nodes = []

    def on_enable(self):
        self.ed.register_handler(self)

    def on_disable(self):
        if self.ed.floating_sprite:
            self.ed.floating_sprite.color = 255, 255, 255
        for node in self.ed.hovered_nodes:
            node.color = 255, 255, 255
        self.ed.unregister_handler(self)

    def on_key_press(self, k, m):

        if k == key.PAGEUP or k == key.PAGEDOWN:
            if k == key.PAGEUP:
                direction = 1
            elif k == key.PAGEDOWN:
                direction = -1

            if self.ed.floating_sprite:
                    # CTRL or COMMAND -> rotate
                if (m & key.MOD_ACCEL):
                    self.ed.rotate_floating(direction)

                    # SHIFT -> opacity
                elif (m & key.MOD_SHIFT):
                    self.ed.change_floating_opacity(direction)

                    # NOTHING -> scale
                else:
                    self.ed.scale_floating(direction)
            else:
                x, y = self.ed.mouse_position
                self.ed.zoom(x, y, direction)

            return True

    def on_mouse_motion(self, px, py, dx, dy):
        x, y = self.ed.layers.pointer_to_world(px, py)
        self.ed.mouse_position = (px, py)

        hovered_nodes = self.ed.current_layer.childrenAt(x, y)
        for node in hovered_nodes:
            if node in self.ed.hovered_nodes:
                self.ed.hovered_nodes.remove(node)
            else:
                if node != self.ed.floating_sprite:
                    node.color = 255, 150, 150
                    self.hovering = node
        for node in self.ed.hovered_nodes:
            if node != self.ed.floating_sprite:
                node.color = 255, 255, 255
        self.ed.hovered_nodes = hovered_nodes

        if not self.ed.hovered_nodes:
            if self.hovering:
                self.hovering = None
                self.ed.propagate_event('hovering_change', self.hovering)

        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            if self.hovering:
                if self.ed.floating_sprite:
                    self.ed.floating_sprite.color = 255, 255, 255
                    self.ed.set_floating(None)
                self.ed.set_floating(self.hovering)
                self.ed.floating_sprite.color = 150, 255, 150
                self.hovering = None
                self.ed.propagate_event('hovering_change', None)
            return True

        if button == 4 or (modifiers & pyglet.window.key.MOD_ACCEL):
            if self.ed.floating_sprite:
                self.ed.floating_sprite.color = 255, 255, 255
                self.ed.set_floating(None)
                return True


    def on_mouse_drag(self, px, py, dx, dy, button, m):
        if button == 1:
            if self.ed.floating_sprite:
                x, y = self.ed.layers.pointer_to_world(px, py)
                nx, ny = self.ed.sprite_grid.snap_to_grid((x, y))
                self.ed.move_floating(nx, ny)
                return True


class EditPlugin(Plugin):
    name = 'edit'

    def __init__(self, editor):
        self.ed = editor
        edit_mode = EditMode(editor)
        editor.register_mode("sprite", edit_mode)

        def get_active():
            'active sprite'
            if editor.floating_sprite:
                return editor.floating_sprite
            if edit_mode.hovering:
                return edit_mode.hovering
            return None
        editor.console.add_mode_variable('edit', 'active', get_active)
