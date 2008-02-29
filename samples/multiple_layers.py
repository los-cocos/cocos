# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

from pyglet import gl

class Square(cocos.layer.Layer):
    def __init__(self, color, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
                
    def step(self, dt):
        gl.glColor4f(*self.color)
        x, y = self.x, self.y
        w = x+self.size; h=y+self.size
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( x, y )
        gl.glVertex2f( x, h )
        gl.glVertex2f( w, h )
        gl.glVertex2f( w, y )
        gl.glEnd()
        gl.glColor4f(1,1,1,1) 
        
if __name__ == "__main__":
    director.init()
    sc = cocos.scene.Scene( 
        *[ Square((0.03*i,0.03*i,0.03*i,1) , i*20, i*20) for i in range(5,20) ]
        )
    sc.add( 5.5, Square((1,0,0,0.5), 150,150, 210 ), "big_one" )
    director.run( sc )