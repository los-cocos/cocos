#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#

"""
Scene class and subclasses
"""
__docformat__ = 'restructuredtext'

__all__ = ['Scene']

from pyglet.gl import *

from director import director
import layer
import cocosnode

class EventHandlerMixin(object):
    def add(self, child, *args, **kwargs):
        super(EventHandlerMixin, self).add(child, *args, **kwargs)
        
        scene = self.get(Scene)
        if not scene: return
        
        if (    scene._handlers_enabled and 
                scene.is_running and 
                isinstance(child, layer) 
                ):
            child.push_handlers()
            
            
    def remove(self, child):
        super(EventHandlerMixin, self).remove(child)
        
        scene = self.get(Scene)
        if not scene: return
        
        if (    scene._handlers_enabled and 
                scene.is_running and 
                isinstance(child, layer) 
                ):
            child.remove_handlers()
            
    
            
 
class Scene(cocosnode.CocosNode, EventHandlerMixin):
    """
    """
   
    def __init__(self, *children):
        """
        Creates a Scene with layers and / or scenes.
        
        Responsibilities:
            Control the dispatching of events to its layers
            
        :Parameters:
            `children` : list of `Layer` or `Scene`
                Layers or Scenes that will be part of the scene.
                They are automatically assigned a z-level from 0 to
                num_children.
        """

        super(Scene,self).__init__()
        self._handlers_enabled = False
        for i, c in enumerate(children):
            self.add( c, z=i )
            
    
            
    def push_all_handlers(self):
        for child in self.get_children():
            if isinstance(child, layer.Layer):
                child.push_handlers()
            
    def remove_all_handlers(self):
        for child in self.get_children():
            if isinstance(child, layer.Layer):
                child.remove_handlers()
    
    def enable_handlers(self, value=True):
        """
        This function makes the scene elegible for receiving events
        """
        if value and not self._handlers_enabled and self.is_running:
            self.push_all_handlers()
        elif not value and self._handlers_enabled and self.is_running:
            self.remove_all_handlers()
        self._handlers_enabled = value
        
        
    def end(self, value=None):
        """Ends the current scene setting director.return_value with `value`
        
        :Parameters:
            `value` : anything
                The return value. It can be anything. A type or an instance.
        """
        director.return_value = value
        director.pop()

