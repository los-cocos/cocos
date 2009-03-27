from cocos.scene import Scene
from cocos.director import director
from cocos.sprite import NotifierSprite
from cocos.layer import Layer
from cocos.actions import *
from cocos.text import Label
from cocos.cocosnode import CocosNode

import pyglet
from pyglet import image
from pyglet import font
from pyglet.window import key
from hud import HUDLayer
from pyglet import gl

import os

import copy

import simplejson

from picker import PickerBatchNode
import atlas
from grid import SpriteGrid
from collision import CollisionLayer

from cocos.euclid import Point2

LACCEL       = key.LCTRL
import sys as _sys
if _sys.platform == 'darwin':
    LACCEL   = key.LCOMMAND


class LayersNode(CocosNode):
    """ This Node promises to have one and only one child at each z """
    def __init__(self):
        super(LayersNode, self).__init__()

    def add_layer(self, name, z, layer_type=PickerBatchNode):
        layer = layer_type()
        layer.label = name
        self.add(layer, name=name, z=z)
        # Normalize z (unique, consecutive and zero-based)
        self.children = [(i, self.children[i][1]) for i in range(len(self.children))]

    def get_by_depth(self, z):
        if z > len(self.children):
            raise ValueError("I only have %d layers" % len(self.children))
        return self.children[z][1]

    def pointer_to_world(self, x, y):
        nx = (x - self.x) / self.scale 
        ny = (y - self.y) / self.scale 

        return nx, ny
    
    def world_to_pointer(self, nx, ny):
        x = nx * self.scale + self.x
        y = ny * self.scale + self.y
        
        return x, y
    

        
class TilessEditor(Layer):
    is_event_handler = True
    def __init__(self, output_filename, tilesdir):
        super(TilessEditor, self).__init__()

        self.output_filename = output_filename
        self.tilesdir = tilesdir

        self.floating_sprite = None
        self.hovered_nodes = []


        # used to add children with a new z every time
        self.increment_z = 0
        
        self.mouse_position = (0, 0)
        
        self.layers = LayersNode()

        for z in range(1, 10):
            self.layers.add_layer("Layer %d" % z, z)
        self.layers.add_layer('Collision Layer', 10, layer_type=CollisionLayer)

        
        self.set_current_layer(0)

        x,y = director.get_window_size()
        self.add(self.layers, z=10)
        self.hud = HUDLayer(self)
        self.add(self.hud, z=100)

        self.pressed_keys = key.KeyStateHandler()
        director.window.push_handlers(self.pressed_keys)

        x, y = director.get_window_size()
        self.sprite_grid = SpriteGrid()
        self.layers.add(self.sprite_grid, z =50)

        from cocos.layer import ColorLayer
        self.hotspot = None

        self.event_handlers = []
        self.plugins = {}
        self.modes = {}
        self.current_mode = None
        
        self.look_at(0,0)
        

    def register_handler(self, handler):
        self.event_handlers.append(handler)

    def unregister_handler(self, handler):
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
        

    def register_plugin(self, plugin_class):
        self.plugins[plugin_class.name] = plugin_class(self)


    def register_mode(self, mode):
        if not self.modes:
            enable = True
        else:
            enable = False
        self.modes[mode.name] = mode
        if enable:
            self.switch_mode(mode.name)

    def switch_mode(self, mode_name):
        print "MODE:", mode_name
        if self.current_mode:
            self.current_mode.on_disable()
        self.current_mode = self.modes[mode_name]
        self.current_mode.on_enable()
        self.propagate_event('mode_changed', mode_name)


    def discard_floating(self):
        self.floating_sprite.parent.remove(self.floating_sprite)
        self.floating_sprite = None
        self.propagate_event('floating_discard')
        
    def set_floating(self, sprite):
        self.floating_sprite = sprite
        self.propagate_event('floating_change', sprite)


    def set_current_layer(self, depth):
        if self.floating_sprite is not None:
            self.current_layer.remove(self.floating_sprite)
            self.floating_sprite = None
        self.current_layer = self.layers.get_by_depth(depth)


    def layer_add_node(self, layer, node):
        self.increment_z += 1
        layer.add(node)
        node.fucking_z = self.increment_z
    

    def propagate_event(self, event_type, *args):
        for handler in self.event_handlers:
            f = getattr(handler, 'on_'+ event_type, None)
            if f:
                r = f(*args)
                if r:
                    break

    def on_key_press(self, k, m):

        if k == key.F1:
            self.switch_mode('edit')
            return True

        if k == key.F2:
            self.switch_mode('camera')
            return True

        if k == key.F3:
            self.switch_mode('stamp')
            return True

        self.propagate_event('key_press', k, m)            

        if k == key.S and (m & pyglet.window.key.MOD_ACCEL):
            file = open(self.output_filename, 'w')
            file.write(self.generate_json())
            file.close()
            return True

        if k == key.L and (m & pyglet.window.key.MOD_ACCEL):
            self.read_json()
            return True

        num_keys = [key._1, key._2, key._3, key._4,
                    key._5, key._6, key._7, key._8, key._9, key._0]

        if k in num_keys and (m & pyglet.window.key.MOD_ACCEL):
            floating_sprite = self.floating_sprite
            self.set_current_layer (num_keys.index(k))
            if not isinstance(self.current_layer, CollisionLayer) and floating_sprite is not None:
                self.floating_sprite = floating_sprite
                self.current_layer.add(self.floating_sprite)

            self.hud.update()
            self.update_hotspot()
            return True


        if k == key.ESCAPE:
            self.update_hotspot()
            return True

        if k == key.DELETE:
            self.update_hotspot()
            return True

        if k == key.Q and (m & pyglet.window.key.MOD_ACCEL):
            director.pop()
            return True

        # WARNING: this key is used only for testing the collisions
        # it is used to trigger the collision detection
        if k==key.C and (m & pyglet.window.key.MOD_ACCEL):
            if isinstance(self.current_layer, CollisionLayer):
                self.current_layer.step()

        # WARNING: this key is used only for testing the collisions
        # it is used to add a static object to the collision space
        # it otherwise acts as the stamp method
        if k==key.A and (m & pyglet.window.key.MOD_ACCEL):
            if isinstance(self.current_layer, CollisionLayer) and self.floating_sprite is not None:
                s = NotifierSprite(self.floating_sprite.image,
                                   (self.floating_sprite.x, self.floating_sprite.y),
                                   self.floating_sprite.rotation,
                                   self.floating_sprite.scale,
                                   self.floating_sprite.opacity)
                s.path = self.floating_sprite.path
                s.rect = self.floating_sprite.rect

                self.increment_z += 1
                self.current_layer.remove(self.floating_sprite)
                self.current_layer.add(self.floating_sprite, static=False)
                s.fucking_z = self.increment_z

                self.last_stamp_pos = self.floating_sprite.position
                self.floating_sprite = s
                self.current_layer.add(self.floating_sprite)

        if k == key.G and (m & pyglet.window.key.MOD_ACCEL):
            if self.sprite_grid.enabled:
                self.sprite_grid.disable()
            elif self.floating_sprite:
                self.sprite_grid.enable(self.floating_sprite)
            elif self.hovering:
                self.sprite_grid.enable(self.hovering)
            else:
                self.sprite_grid.disable()
            return True                

    def on_enter(self):
        self.propagate_event('enter')
        super(TilessEditor, self).on_enter()
            
    def on_exit(self):
        super(TilessEditor, self).on_exit()
        if self.floating_sprite:
            self.current_layer.remove(self.floating_sprite)
            self.floating_sprite = None
        
    def on_mouse_motion(self, px, py, dx, dy):
        self.propagate_event('mouse_motion', px, py, dx, dy)
        self.hud.update()

    def on_mouse_press(self, x, y, button, m):
        self.propagate_event('mouse_press', x, y, button, m)
        self.update_hotspot()
        

    def update_hotspot(self):
        pass
#        if self.hotspot is not None:
#            self.remove(self.hotspot)
#            self.hotspot = None
#        if self.hovering is not None:
#            hotspot = self.current_layer.picker.hotspot(self.hovering)
#            if self.hotspot is not None:
#                self.remove(self.hotspot)
#                self.hotspot = None
#            from cocos.layer import ColorLayer
#            width = int((hotspot[2] - hotspot[0])*self.layers.scale)
#            height = int((hotspot[3]-hotspot[1])*self.layers.scale)
#            self.hotspot = ColorLayer(255, 150, 150, 255, width, height)
#            self.add(self.hotspot)
#            x = hotspot[0]*self.layers.scale + self.layers.x
#            y = hotspot[1]*self.layers.scale+self.layers.y
#            self.hotspot.position = x, y


    def on_mouse_drag(self, px, py, dx, dy, button, m):
        self.propagate_event('mouse_drag', px, py, dx, dy, button, m)
                    
    def on_mouse_release(self, x, y, button, m):
        self.propagate_event('mouse_release', x, y, button, m)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.propagate_event("mouse_scroll", x, y, scroll_x, scroll_y)
        self.update_hotspot()


    def move_floating(self, nx, ny):
        self.floating_sprite.position = (nx, ny)
        self.propagate_event('floating_change', self.floating_sprite)
    
    def rotate_floating(self, scroll_y):
        if scroll_y>0: sign = 1
        else: sign = -1
        amount = -5*sign
        self.floating_sprite.rotation += amount
        self.propagate_event('floating_change', self.floating_sprite)
        
    def change_floating_opacity(self, scroll_y):
        opacity = self.floating_sprite.opacity
        if scroll_y < 0:
            new_opacity = opacity * 0.9
        else:
            new_opacity = opacity * 1.1
        if new_opacity > 255: new_opacity = 255
        self.floating_sprite.opacity = new_opacity
        self.propagate_event('floating_change', self.floating_sprite)

    def scale_floating(self, scroll_y):
        amount = 1
        if scroll_y < 0: amount = 0.9
        else: amount = 1.1
        self.floating_sprite.scale *= amount
        self.propagate_event('floating_change', self.floating_sprite)

        
    def zoom(self, x, y, scroll_y):
        wx, wy = self.layers.pointer_to_world(x,y)
        self.layers.scale *= 1.3**scroll_y
        nwx, nwy = self.layers.pointer_to_world(x,y)
        dx = (wx - nwx) * self.layers.scale
        dy = (wy - nwy) * self.layers.scale
        self.layers.x -= dx
        self.layers.y -= dy
        
    def look_at(self, x, y):
        xs, ys = director.get_window_size()
        self.layers.x = -(x * self.layers.scale) + xs/2
        self.layers.y = -(y * self.layers.scale) + ys/2
        
    def generate_json(self):
        layers = {}
        for z, layers_node in self.layers.children:
            layers[z] = {}
            sprites = []
            for i, c in layers_node.children:
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
            if hasattr(layers_node,'label'):
                layers[z]['name'] = layers_node.label
            layers[z]['sprites'] = sprites
        result = dict(tilesdir=self.tilesdir, layers=layers)
        return simplejson.dumps(result)


    def read_json(self):
        layers_dict = simplejson.load(open(self.output_filename))['layers']

        def build_sprite(img):
            s = Sprite(str(img['filename']),
                       img['position'], img['rotation'], img['scale'], img['opacity'])
            s.label = img['label'] if "label" in img else None
            s.path = img['filename']
            s.rect =img['rect']
            return s

        for z in range(1, 10):
            name = "Layer %d" % z
            current_layer = layers_dict.get(name)
            for img in current_layer:
                s = build_sprite(img)
                layer = self.layers.get( name )
                self.layer_add_node(layer, s)
        # collision layer
        name = "Collision Layer" 
        current_layer = layers_dict.get(name)
        for img in current_layer:
            s = build_sprite(img)
            layer = self.layers.get( name )
            self.layer_add_node(layer, s)

        self.set_current_layer(0)

    def __repr__(self):
        return "<Editor>"


if __name__ == '__main__':

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option("-f", "--filename", dest="filename", default='map.json',
                      help="output filename", metavar="FILE")
    parser.add_option("-t", "--tilesdir", dest="tilesdir", default='tiles/set4',
                      help="tiles folder", metavar="FOLDER")
    parser.add_option("-F", "--fullscreen", dest="fullscreen", default=False,
                      help="set fullscreen mode on", action="store_true")
    parser.add_option("-x", "--width", dest="width", default='800',
                      help="set window width", metavar="WIDTH")
    parser.add_option("-y", "--height", dest="height", default='600',
                      help="set window height", metavar="HEIGHT")
    
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    
    if options.fullscreen:
        director.init(fullscreen=options.fullscreen)
    else:
        director.init(width=int(options.width), height=int(options.height))

    editor = TilessEditor(options.filename, options.tilesdir)
    editor_scene =  Scene(editor)

    from plugins import editor_console, camera, stamp, edit

    editor.register_plugin(editor_console.ConsolePlugin)
    editor.register_plugin(edit.EditPlugin)
    editor.register_plugin(camera.CameraPlugin)
    editor.register_plugin(stamp.StampPlugin)

    director.run(editor_scene)
