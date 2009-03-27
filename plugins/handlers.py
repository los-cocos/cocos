from pyglet.window import key

from plugin import EventHandler

# WARNING: This is a MixIn class. It assumes a self.ed attribute, which should be
# a TilessEditor instance.
class MouseEventHandler(EventHandler):

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            direction = 1
        elif scroll_y < 0:
            direction = -1

        if self.ed.floating_sprite:
            # CTRL or COMMAND -> rotate
            if (key.LCOMMAND in self.ed.pressed_keys or key.LCTRL in self.ed.pressed_keys) \
                and (self.ed.pressed_keys[key.LCOMMAND] or self.ed.pressed_keys[key.LCTRL]):
                self.ed.rotate_floating(direction)

            # SHIFT -> opacity
            elif key.LSHIFT in self.ed.pressed_keys and self.ed.pressed_keys[key.LSHIFT] == True:
                self.ed.change_floating_opacity(direction)

            # NOTHING -> scale
            else:
                self.ed.scale_floating(direction)
        else:
            x, y = self.ed.mouse_position
            self.ed.zoom(x, y, direction)

        return True

