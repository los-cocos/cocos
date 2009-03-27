from math import radians    

import cocos
import pyglet
from cocos import euclid

from pyglet.gl import glPushMatrix, glPopMatrix
from cocos.director import director

class SpriteGrid(cocos.cocosnode.CocosNode):
    def __init__(self, color=None):
        super(SpriteGrid, self).__init__()
        self.color = color
        if color is None:
            self.color = 50,200,50,100
        self.enabled = False
        self.matrix = None
        
    def enable(self, sprite=None):
        self.enabled = True
        if sprite:
            self.grid_scale = sprite.scale
            self.rotation = sprite.rotation
            self.matrix = euclid.Matrix3.new_rotate(radians(self.rotation))
            self.inverse = euclid.Matrix3.new_rotate(radians(-self.rotation))
            
            self.width = sprite.width
            self.height = sprite.height
            sx = sprite.x - int(self.width/2)
            sy = sprite.y - int(self.height/2)
            
            self.position = sprite.position
            self.build_lines()
            
            self.inverse.scale(1.0/self.scale, 1.0/self.scale)
            
    def snap_to_grid(self, position):
        if not self.enabled:
            return position
        
        #x, y = self.matrix * euclid.Point2(*position)
        x, y = position
        sx, sy = self.position
        
        dx = x - sx
        dy = y - sy
        
        dx, dy = self.matrix * euclid.Point2(dx, dy)
        dx += self.width/2
        dy += self.height/2
        
        fx = (dx//self.width)*self.width
        fy = (dy//self.height)*self.height
        return (self.inverse * euclid.Point2(fx, fy)) + \
                    euclid.Point2(sx, sy)
    
    def disable(self):
        self.enabled = False
        
    def build_lines(self):
        vertical = []
        for x in range(-100,100):
            xv = self.width*x - self.width/2
            vertical.append(xv)
            vertical.append(self.position[1] - self.height*50)
            vertical.append(xv)
            vertical.append(self.position[1] + self.height*50)
            
        horiz = []
        for y in range(-100,100):
            yv = self.height*y - self.height/2
            horiz.append(self.position[0] - self.width*50)
            horiz.append(yv)
            horiz.append(self.position[0] + self.width*50)
            horiz.append(yv)
            
        self.vertex = pyglet.graphics.vertex_list(len(vertical+horiz)/2,
            ('v2f', vertical+horiz),
            ('c4B', self.color*(len(vertical+horiz)/2))
        )
        
    def draw(self):
        glPushMatrix()
        self.transform()
        if self.enabled:
            self.vertex.draw(pyglet.gl.GL_LINES)
            
        glPopMatrix()
        