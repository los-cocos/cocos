from director import director
from pyglet.gl import *
from pyglet import image

class Effect(object):
    """Base class for effects. Effects are applied to layers (or
    anything that is shown with a step (dt) method). Useful effects can
    inherit this one, which is just the identity effect"""
    
    def prepare (self, target, dt):
        """Advance target in dt, preparing effect display."""
        self.target = target
        self.dt = dt
    
    def show (self):
        """Show on screen"""
        self.target.step (self.dt)

class TextureFilterEffect (Effect):

    """Base class for texture based effects. Prepare setups self.texture,
    with a window sized capture. Show just blits the texture, override to
    do more interesting things"""
    def __init__ (self):
        self.texture = image.Texture.create_for_size(GL_TEXTURE_2D, 
            director.window.width, director.window.height, GL_RGB)
        self.texture = self.texture.get_region(0, 0, director.window.width, director.window.height)

    def prepare (self, target, dt):
        director.window.clear()
        target.step (dt)
        buffer = image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)
            
    def show (self):
        self.texture.blit (0, 0)

