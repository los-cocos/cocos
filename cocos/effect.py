"""Effects that can be applied to layers.

Effect
======

Effect are visual transformations that can be applied to layers. You normally
use them by calling the ``cocos.layer.Layer.set_effect`` method on a layer,
passing an effect as argument (or None to disable the effect).

This module provides some Effect classes which are ready to use:

 - ColorizeEffect: Multiplicative filter of color/alpha
 - RepositionEffect: Resize/relocate layer
 
And some abstract base classes to define your own effects:

 - Effect: The base class for every effect
 - TextureFilterEffect: Captures the layer into a texture, allowing you to
    display it in any way that a texture can be used.

An effect object should not be applied to several layers at once.

"""

__docformat__ = 'restructuredtext'

from director import director
from pyglet import image

from pyglet.gl import *
from framegrabber import TextureGrabber

__all__ = ['Effect', 'TextureFilterEffect','ColorizeEffect', 'RepositionEffect']

class Effect(object):
    """Abstract base class for effects. Effects are applied to layers (or
    anything that is shown with a draw() method). Useful effects can
    inherit this one, which is just the identity effect"""
    
    def prepare (self, target):
        """Advance target in dt, preparing effect display."""
        self.target = target
    
    def show (self):
        """Show layer+effect on screen"""
        self.target.draw()

class TextureFilterEffect (Effect):
    """Base class for texture based effects. Prepare captures layer in
    ``self.texture``,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things"""
    def __init__ (self):
        w, h = director.window.get_size()
        print "TextureFilterEffect(%d,%d)" % (w,h)
        self.texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            w, h, GL_RGBA)
        
        self._grabber = TextureGrabber()
        self._grabber.grab (self.texture)
        
        self.texture = self.texture.get_region(0, 0, w, h)

    def prepare (self, target):
        self._grabber.before_render(self.texture)
        target.batch.draw()
        target.draw()
        self._grabber.after_render(self.texture)
            
    def show (self):
        """``self.texture`` contains the layer; redefine this method to
        show the texture applying the effect you want."""
        self.texture.blit (0, 0)

class ColorizeEffect (TextureFilterEffect):
    """Applies recoloring (multiplication) and alpha blending."""
    def __init__ (self, color=(1,1,1,1)):
        """
        New colorize effect.
        ``color`` is stored in ``self.color``, which can be modified later.

        :Parameters:    
            `color` : a 4-uple (red, green, blue, alpha) of floats in 0.0-1.0 range
                The color that will be multiplied by the layer colors.

        """
        super (ColorizeEffect, self).__init__ ()
        self.color = color

    def show (self):
        """Blits ``self.texture`` calling glColor4f before with ``self.color``."""
        glColor4f (*self.color)
        self.texture.blit (0, 0)
        glColor4f (1,1,1,1)

class RepositionEffect (TextureFilterEffect):
    """Applies repositioning and scaling"""
    def __init__ (self, x=0, y=0, width=None, height=None):
        """
        New reposition effect.        
        Parameters are stored in ``self.x``, ``self.y``, ``self.width``,
        ``self.height``, which can be modified later.
        
        :Parameters:
            `x` : Integer
                The horizontal shift for the layer (default=0)
            `y` : Integer
                The vertical shift for the layer (default=0)
            `width` : Integer
                The horizontal size for the layer (default=0)
            `height` : Integer
                The vertical size for the layer (default=0)

        """
        super (RepositionEffect, self).__init__ ()
        self.x = x
        self.y = y
        if width is None: width = self.texture.width
        if height is None: height = self.texture.height
        self.width = width
        self.height = height

    def show (self):
        """Blits ``self.texture`` at the rectangle defined by 
        ``self.x``, ``self.y``, ``self.width``, ``self.height``"""
        self.texture.blit (self.x, self.y, width=self.width, height=self.height)

