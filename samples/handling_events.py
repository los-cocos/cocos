from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director

import pyglet


class KeyDisplay(cocos.layer.Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__(self):

        super(KeyDisplay, self).__init__()

        self.text = cocos.text.Label("", x=100, y=280)

        # To keep track of which keys are pressed:
        self.keys_pressed = set()
        self.update_text()
        self.add(self.text)

    def update_text(self):
        key_names = [pyglet.window.key.symbol_string(k) for k in self.keys_pressed]
        text = 'Keys: ' + ','.join(key_names)
        # Update self.text
        self.text.element.text = text

    def on_key_press(self, key, modifiers):
        """This function is called when a key is pressed.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)

        See also on_key_release situations when a key press does not fire an
         'on_key_press' event.
        """
        self.keys_pressed.add(key)
        self.update_text()

    def on_key_release(self, key, modifiers):
        """This function is called when a key is released.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)

        Constants are the ones from pyglet.window.key

        Sometimes a key release can arrive without a previous 'press' event, so discard
        is used instead of remove.

        This can happen in Windows by example when you 'press ALT, release ALT, press B,
        release B'; the events received are 'pressed ALT, released ALT, released B'.

        This may depend on the pyglet version, here pyglet from repo at may 2014 was used.
        """
        self.keys_pressed.discard(key)
        self.update_text()


class MouseDisplay(cocos.layer.Layer):

    # If you want that your layer receives events
    # you must set this variable to 'True',
    # otherwise it won't receive any event.
    is_event_handler = True

    def __init__(self):
        super(MouseDisplay, self).__init__()

        self.posx = 100
        self.posy = 240
        self.text = cocos.text.Label('No mouse events yet', font_size=18, x=self.posx, y=self.posy)
        self.add(self.text)

    def update_text(self, x, y):
        text = 'Mouse @ %d,%d' % (x, y)
        self.text.element.text = text
        self.text.element.x = self.posx
        self.text.element.y = self.posy

    def on_mouse_motion(self, x, y, dx, dy):
        """Called when the mouse moves over the app window with no button pressed
        
        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        """
        self.update_text(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Called when the mouse moves over the app window with some button(s) pressed
        
        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.update_text(x, y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.posx, self.posy = director.get_virtual_coordinates(x, y)
        self.update_text(x, y)


if __name__ == "__main__":
    director.init(resizable=True)
    # Run a scene with our event displayers:
    director.run(cocos.scene.Scene(KeyDisplay(), MouseDisplay()))
