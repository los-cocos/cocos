from collision import CollisionLayer
from plugin import Plugin
from plugins.sprite_layer import SpriteLayerFactory
from plugins.edit import EditMode
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
        stamp_mode = StampMode(editor)
        editor.register_layer_factory("collision", self.factory)
        editor.register_mode("collision", stamp_mode)
        editor.register_mode("collision", edit_mode)
