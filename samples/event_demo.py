# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director

import pyglet
from pyglet import font

class KeyDisplay(cocos.layer.Layer):
    def __init__(self):
        self.font = font.load('Arial', 24)
        # To keep track of which keys are pressed:
        self.keys_pressed = set()
        self.update_text()
        
    def step(self, dt):
        self.text.draw()

    def on_key_press (self, key, modifiers):
        """This function is called when a key is pressed.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)
            
        """
        self.keys_pressed.add (key)
        self.update_text()

    def on_key_release (self, key, modifiers):
        """This function is called when a key is released.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)

        Constants are the ones from pyglet.window.key
        """
        self.keys_pressed.remove (key)
        self.update_text()

    def update_text(self):
        key_names = [pyglet.window.key.symbol_string (k) for k in self.keys_pressed]
        text = 'Keys: '+','.join (key_names)
        # Update self.text
        self.text = font.Text(self.font, text, x=100, y=280)

class MouseDisplay(cocos.layer.Layer):
    def __init__(self):
        self.font = font.load('Arial', 24)
        self.x = 100
        self.y = 240
        self.text = font.Text(self.font, 'No mouse events yet', x=self.x, y=self.y)
        
    def step(self, dt):
        self.text.draw()

    def on_mouse_motion (self, x, y, dx, dy):
        """This function is called when the mouse is moved over the app.
        
        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        """
        self.update_text (x, y)

    def on_mouse_press (self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.x, self.y = director.get_virtual_coordinates (x, y)
        self.update_text (x,y)

    def update_text (self, x, y):
        text = 'Mouse @ %d,%d' % (x, y)
        self.text = font.Text(self.font, text, x=self.x, y=self.y)

if __name__ == "__main__":
    director.init(resizable=True)
    # Run a scene with our event displayers:
    director.run( cocos.scene.Scene( KeyDisplay(), MouseDisplay() ) )
