import pyglet
from pyglet.window import key
from pyglet.window import mouse

import cocos

class ButtonsKBDController(cocos.layer.Layer):
    """
    Simulates a device with an array of user defined buttons.
    Updates the button status (0/1, meaning pressed - not pressed) by
    listening to keyboard events.
    Which key maps to which button is defined by the dictionary bindings
    received in __init__
    User code access button status by reading from the member 'buttons', a
    dictionary of <button name>: <state 0/1> value pairs
    """
    is_event_handler = True

    def __init__(self, bindings):
        """
        bindings: dict with <pyglet key code>: <button name> key value pairs
        for the keys this controller should handle.
        Example bindings:
        from pyglet.window import key
        bindings = {
            key.LEFT: 'left',
            key.RIGHT: 'right',
            }        
        """
        self.bindings = bindings
        buttons = {}
        for k in bindings:
            buttons[bindings[k]] = 0
        self.buttons = buttons

    def on_key_press(self, k, m):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False
        
