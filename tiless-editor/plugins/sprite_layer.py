from plugin import LayerFactory, Plugin
from picker import PickerBatchNode
from cocos.sprite import NotifierSprite

class SpriteLayerFactory(LayerFactory):
    def get_new_layer(self):
        layer = PickerBatchNode()
        layer.layer_type = "sprite"
        return layer

    def layer_to_dict(self, layer):
        sprites = []
        for i, c in layer.children:
            label = getattr(c, "label", None)
            sprites.append(dict(position=c.position,
                                 scale=c.scale,
                                 rotation=c.rotation,
                                 opacity=c.opacity,
                                 filename=c.path,
                                 label=label,
                                 z=0,
                                 rect=c.rect,
                                 ))
        return dict(sprites=sprites)

    def dict_to_layer(self, in_dict):
        def build_sprite(img):
            s = NotifierSprite(str(img['filename']),
                       img['position'], img['rotation'], img['scale'], img['opacity'])
            s.label = img['label'] if "label" in img else None
            s.path = img['filename']
            s.rect =img['rect']
            return s

        layer = self.get_new_layer()
        for item in in_dict["sprites"]:
            sprite = build_sprite(item)
            layer.add(sprite)
        return layer

class SpriteLayerPlugin(Plugin):
    name = 'sprite_layer'

    def __init__(self, editor):
        self.ed = editor
        self.factory = SpriteLayerFactory()
        editor.register_layer_factory("sprite", self.factory)
