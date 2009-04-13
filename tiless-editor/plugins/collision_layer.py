import os.path

import atlas

from layers.collision import CollisionLayer
from plugin import Plugin
from plugins.edit import EditMode
from plugins.camera import CameraMode
from plugins.sprite_layer import SpriteLayerFactory
from plugins.stamp import StampMode


class CollisionLayerFactory(SpriteLayerFactory):
    def get_new_layer(self):
        layer = CollisionLayer()
        layer.layer_type = "collision"
        return layer


class CollisionLayerPlugin(Plugin):
    name = 'collision_layer'

    def __init__(self, editor):
        self.ed = editor
        self.factory = CollisionLayerFactory()
        edit_mode = EditMode(editor)
        stamp_mode = CollisionStampMode(editor)
        camera_mode = CameraMode(editor)
        editor.register_layer_factory("collision", self.factory)
        editor.register_mode("collision", collision_mode)
        editor.register_mode("collision", edit_mode)
        editor.register_mode("collision", camera_mode)


class CollisionStampMode(StampMode):
    name = 'stamp'

    def __init__(self, editor):
        super(CollisionMode, self).__init__(editor)
        collision_tiles_dir = os.path.join(self.ed.tilesdir, '../collision')
        self.atlas = atlas.TextureAtlas(collision_tiles_dir)
        self.atlas.fix_image()

