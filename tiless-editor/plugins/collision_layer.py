from cocos.sprite import NotifierSprite
from pyglet.window import key

import os.path

import atlas

from layers.collision import CollisionLayer
from plugin import Plugin, EventHandler
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

        edit_mode = CollisionEditMode(editor)
        stamp_mode = CollisionStampMode(editor)
        camera_mode = CollisionCameraMode(editor)
        editor.register_layer_factory("collision", self.factory)
        editor.register_mode("collision", edit_mode)
        editor.register_mode("collision", camera_mode)
        editor.register_mode("collision", stamp_mode)


class CollisionEventHandler(EventHandler):
    def on_key_press(self, k, m):
        if k == key.D and (m & key.MOD_ACCEL):
            # toggle shapes on/off for debugging
            self.ed.current_layer.show_shapes = not self.ed.current_layer.show_shapes
            return True
        elif k==key.C and (m & key.MOD_ACCEL):
            # trigger collision detection
            self.ed.current_layer.step()
            return True
        elif k==key.A and (m & key.MOD_ACCEL):
            # add a static object to the collision space
            if self.ed.floating_sprite is not None:
                floating_sprite = self.ed.floating_sprite
                s = NotifierSprite(floating_sprite.image,
                                   (floating_sprite.x, floating_sprite.y),
                                   floating_sprite.rotation,
                                   floating_sprite.scale,
                                   floating_sprite.opacity)
                s.path = floating_sprite.path
                s.rect = floating_sprite.rect

                self.ed.current_layer.remove(floating_sprite)
                self.ed.current_layer.add(floating_sprite, static=False)

                self.last_stamp_pos = floating_sprite.position
                self.ed.floating_sprite = s
                self.ed.current_layer.add(self.ed.floating_sprite)
                return True
        # if the event was not handled so far, continue with the other handlers
        return super(CollisionEventHandler, self).on_key_press(k, m)



class CollisionEditMode(CollisionEventHandler, EditMode): pass


class CollisionCameraMode(CollisionEventHandler, CameraMode): pass


class CollisionStampMode(CollisionEventHandler, StampMode):
    def __init__(self, editor):
        super(CollisionStampMode, self).__init__(editor)
        collision_tiles_dir = os.path.join(self.ed.tilesdir, '../collision')
        self.atlas = atlas.TextureAtlas(collision_tiles_dir)
        self.atlas.fix_image()

