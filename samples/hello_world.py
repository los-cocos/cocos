# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

from pyglet import font

class HelloWorld(cocos.layer.Layer):
    def __init__(self):
        ft = font.load('Arial', 36)
        self.text = font.Text(ft, 'Hello, World!', x=100, y=240)
        
    def step(self, dt):
        self.text.draw()

if __name__ == "__main__":
    director.init()
    director.run( cocos.scene.Scene( HelloWorld() ) )