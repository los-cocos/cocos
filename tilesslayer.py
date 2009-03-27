# ----------------------------------------------------------------------------
# cocos2d
# ----------------------------------------------------------------------------
'''
TilessLayer
'''

__docformat__ = 'restructuredtext'

# cocos2d
import cocos
from cocos.cocosnode import *
from cocos.director import director
from cocos.actions import Accelerate, Rotate
from cocos.sprite import Sprite, BatchNode
import pyglet
from pyglet import gl

from pyglet.image.atlas import Allocator

# python
import simplejson
import os


__all__ = [ 'TilessLayer',                     # Sprite class
            ]

class MyAllocator(Allocator):

    def alloc(self, width, height):

        # create an Atlas with 1 pixel of border
        width += 1
        height += 1
        return super(MyAllocator,self).alloc(width, height)


class TilessLayer( CocosNode ):
    '''Sprites are sprites that can execute actions.

    Example::

        layer = TilessLayer('map.json')
    '''

    def __init__( self, jsonfile, atlasfile ):
        '''Initialize the TilessLayer

        :Parameters:
                `jsonfile` : string
                    json file that contains the tiless values
                `atlasfile` : string
                    texture atlas files
        '''
        super(TilessLayer,self).__init__()

        self.texture = None
        self.vertex_list = None

        self.load_atlas( atlasfile )
        self.parse_json_file( jsonfile )

    def load_atlas( self, atlasfile ):
        img = pyglet.image.load( atlasfile )
        self.atlas = pyglet.image.atlas.TextureAtlas( img.width, img.height )
        self.atlas.texture = img.texture
        gl.glTexParameteri( img.texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE )
        gl.glTexParameteri( img.texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE )

    def parse_json_file( self, jsonfile ):
        '''data parser'''

        layers_dict = simplejson.load(open( jsonfile ))['layers']

        for key in layers_dict.keys():
            current_layer = layers_dict[key]
            batch = BatchNode()

            sprites = current_layer.get('sprites',[])
            for sprite in sprites:
                rect = sprite['rect']
                region = pyglet.image.TextureRegion( rect[0], rect[1], 0, rect[2], rect[3], self.atlas.texture )

                s = Sprite( region, sprite['position'], sprite['rotation'], sprite['scale'], sprite['opacity'])
                if "label" in sprite:
                    s.label = sprite['label']

                batch.add( s )
            self.add( batch )


if __name__ == "__main__":
    director.init(width=800, height=600, fullscreen=False)
    test_layer = TilessLayer('map.json', 'atlas-fixed.png')
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
