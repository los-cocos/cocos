#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Layer class and subclasses

A `Layer` has as size the whole drawable area (window or screen),
and knows how to draw itself. It can be semi transparent (having holes
and/or partial transparency in some/all places), allowing to see other layers
behind it. Layers are the ones defining appearance and behavior, so most
of your programming time will be spent coding Layer subclasses that do what
you need. The layer is where you define event handlers.
Events are propagated to layers (from front to back) until some layer catches
the event and accepts it.
"""

__docformat__ = 'restructuredtext'

import pyglet
from pyglet.gl import *
from pyglet.window import key

from director import *
import cocosnode
import scene
import bisect
import sys

__all__ = [ 'Layer', 'MultiplexLayer', 'ColorLayer', 'InterpreterLayer' ]

class Layer(cocosnode.CocosNode, scene.EventHandlerMixin):
    """Class that handles events and other important game's behaviors"""

    is_event_handler = False #! if true, the event handlers of this layer will be registered. defaults to false.
    
    def __init__( self ):
        super( Layer, self ).__init__()
        self.scheduled_layer = False
    
    def push_handlers(self):
        if self.is_event_handler:
            director.window.push_handlers( self )
        for child in self.get_children():
            if isinstance(child, Layer):
                child.push_handlers()
                
    def remove_handlers(self):
        if self.is_event_handler:
            director.window.remove_handlers( self )
        for child in self.get_children():
            if isinstance(child, Layer):
                child.remove_handlers()
           
    def on_enter(self):
        super(Layer, self).on_enter()
        
        scn = self.get(scene.Scene)
        if not scene: return
        
        if scn._handlers_enabled:
            director.window.push_handlers( self )
        
    def on_exit(self):
        super(Layer, self).on_exit()
        
        scn = self.get(scene.Scene)
        if not scene: return
        
        if scn._handlers_enabled:
            director.window.remove_handlers( self )

#
# MultiplexLayer
class MultiplexLayer( Layer ):
    """A Composite layer that only enables one layer at the time.

     This is useful, for example, when you have 3 or 4 menus, but you want to
     show one at the time"""

    
    def __init__( self, *layers ):
        super( MultiplexLayer, self ).__init__()

        self.layers = layers 
        self.enabled_layer = 0

        self.add( self.layers[ self.enabled_layer ] )

    def switch_to( self, layer_number ):
        """Switches to another Layer that belongs to the Multiplexor.

        :Parameters:
            `layer_number` : Integer
                MUST be a number between 0 and the quantities of layers - 1.
                The running layer will receive an "on_exit()" call, and the
                new layer will receive an "on_enter()" call.
        """
        if layer_number < 0 or layer_number >= len( self.layers ):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        self.remove( self.layers[ self.enabled_layer ] )

        self.enabled_layer = layer_number
        self.add( self.layers[ self.enabled_layer ] )



class QuadNode(cocosnode.CocosNode):
    def __init__(self, color):
        super(QuadNode, self).__init__()

        self.batch = pyglet.graphics.Batch()
        self.color = color
        
    def on_enter(self):
        super(QuadNode, self).on_exit()
        x, y = director.get_window_size()
        
        self.vertex_list = self.batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', (0, 0, 0, y, x, y, x, 0)),
            ('c4B', self.color*4)
        )
    
    def on_exit(self):
        super(QuadNode, self).on_exit()
        self.vertex_list.delete()
        
    def on_draw(self):
        self.batch.draw()
        
    

class ColorLayer(Layer):
    """Creates a layer of a certain color.
    The color shall be specified in the format (r,g,b,a).
    
    For example, to create green layer::
    
        l = ColorLayer(0, 255, 0, 0 )
    """
    def __init__(self, *color):
        super(ColorLayer, self).__init__()
        self.add( QuadNode(color) )

class InterpreterLayer(Layer):
    """Creates a python interpreter that uses the sames globals() and locals() variables as sefl.
    This is useful to debug and test new features.

    Example::

        scene.add( InterpreterLayer() )        

        or you can activate it with CTRL +'i' ( COMMAND + i in Mac)
    """
    def __init__(self):
        super(Layer,self).__init__()
        self.cmd = ''
        self.ignore_text = False
        self.local_vrbl = locals()
        self.global_vrbl = globals()

        self._cmd = pyglet.text.Label('>>> ',x=0,y=5)
        w,h = director.get_window_size()
        self._output = pyglet.text.Label('', valign=pyglet.font.Text.BOTTOM,x=0,y=20,multiline=True,width=w)

    def on_text(self, text):
        if not self.ignore_text:
            self.cmd += text
        else:
            self.ignore_text = False
        return True

    def on_draw( self ):
        self._cmd.text = '>>> ' + self.cmd
        self._cmd.draw()
        self._output.draw()

    def on_key_press( self, symbol, m):
        if symbol == key.BACKSPACE:
            if self.cmd:
                self.cmd = self.cmd[:-1]
            return True
        elif symbol == key.ENTER:
            old_stdout = sys.stdout
            sys.stdout = FileStream()
            try:
                obj = compile( '%s' % self.cmd, '<string>','single')
                self._output.text +='%s\n' % self.cmd
                exec obj in self.global_vrbl, self.local_vrbl
                self._output.text += '%s\n' % sys.stdout._data
            except Exception,e:
                self._output.text += '%s\n' % str(e)

            # have a small output
            self._output.text = self._output.text[-1000:]
            self.cmd =''
            self.ignore_text = True
            sys.stdout = old_stdout

            return True

class FileStream( object ):
    def __init__(self):
        super(FileStream,self).__init__()
        self._data = ''

    def write( self, d ):
        self._data = '%s%s' % ( self._data, d )

    def get_data(self):
        return self._data

    def flush( self ):
        self._data = ''
