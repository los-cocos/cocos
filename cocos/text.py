from director import director
import cocosnode
from batch import *

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet import image
from pyglet.gl import *

from batch import *

class TextElement(cocosnode.CocosNode):
    def __init__(self, text='', position=(0,0), **kwargs):
        super(TextElement, self).__init__()
        self.position = position
        self.args = []
        self.kwargs = kwargs
        kwargs['text']=text
        self.group = None
        self.batch = None
        
        self.batch = pyglet.graphics.Batch()
        self.create_element()
        
    def create_element(self):
        self.element = self.klass(group=self.group, batch=self.batch, **self.kwargs)
        
    def on_draw(self):
        glPushMatrix()
        self.transform()
        self.element.draw()
        glPopMatrix()
        
class Label(TextElement):
    klass = pyglet.text.Label
    
class HTMLLabel(TextElement):
    klass = pyglet.text.HTMLLabel
