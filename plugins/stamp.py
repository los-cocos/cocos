from math import atan, degrees

from pyglet import gl
from pyglet.window import key

from cocos.layer import Layer
from cocos.director import director
from cocos.actions import *
from cocos.scene import Scene
from cocos.sprite import NotifierSprite


import atlas
from plugin import Plugin, Mode
from plugins.handlers import MouseEventHandler

class ImgSelector(Layer):
    
    is_event_handler = True

    def __init__(self, tilesdir, grid_size=200, padding_percent=10):
        super(ImgSelector, self).__init__()

        self.grid_size = grid_size
        self.padding_percent = padding_percent
        self.h_slots = (director.window.width / self.grid_size)

        self.atlas = atlas.TextureAtlas(tilesdir)
        self.atlas.fix_image()

        gl.glTexParameteri( self.atlas.texture.target,
                            gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE )
        gl.glTexParameteri( self.atlas.texture.target,
                            gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE )


        self.node_list = self.atlas.sprites

        map(self.add, self.node_list)
        self.position_nodes()
        self.current_node = None

    def position_nodes(self):
        initial_slot = ((self.grid_size / 2),
                        (director.window.height - self.grid_size / 2))
        x_count = 0
        y_count = 0
        for node in self.node_list:
            node.hilighted = False
            if x_count == self.h_slots:
                x_count = 0
                y_count += 1
            node.x = initial_slot[0] + (x_count * self.grid_size)
            node.y = initial_slot[1] - (y_count * self.grid_size)

            scale_magnitude = float(self.grid_size - \
                                    (self.grid_size * self.padding_percent/100))\
                                    / (node.height|node.width)
            node.do(ScaleBy(scale_magnitude, 0.1))

            x_count += 1

    def scroll_page(self, scroll_y): 
        if self.y <= 0 and scroll_y == 1:
            return
        else:
            displacement = scroll_y * self.grid_size * -1
            self.do(MoveBy((0, displacement), 0.1))


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll_page(scroll_y)

    def on_key_press(self, k, m):
        if k in [key.PLUS, key.EQUAL, key.MINUS]:

            if k in [key.PLUS, key.EQUAL] and self.h_slots > 1:
                self.h_slots -= 1

            elif k == key.MINUS and self.h_slots < 15:
                self.h_slots += 1


            self.grid_size = director.window.width / self.h_slots
            self.position_nodes()

        if k == key.ESCAPE:
            director.pop()
            return True

        if k == key.PAGEUP or k == key.PAGEDOWN:
            if k == key.PAGEUP: scroll_y = 1
            elif k == key.PAGEDOWN: scroll_y = -1
            self.scroll_page(scroll_y)

    def on_mouse_motion(self, px, py, dx, dy):
        hilight = ScaleBy(1.2, 0.1)
        for node in self.node_list:
            x, y = node.x + self.x, node.y + self.y
            mouse_over = (px-x)**2+(py-y)**2 < ((self.grid_size-self.padding_percent/2)/2)**2
            if mouse_over and not self.current_node == node:
                node.do(hilight)
                node.hilighted = True
                self.current_node = node

            elif not mouse_over and node.hilighted:
                node.hilighted = False
                node.do(Reverse(hilight))
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1 and self.current_node:
            director.scene.end(self.current_node)


class StampMode(Mode, MouseEventHandler):
    name = 'stamp'
    
    def __init__(self, editor):
        self.ed = editor
        self.drag_x = 0
        self.drag_y = 0
        
    def on_enable(self):
        self.ed.register_handler(self)
        if not self.ed.floating_sprite:
            director.push(Scene(ImgSelector(self.ed.tilesdir)))


    def on_disable(self):
        if self.ed.floating_sprite:
            self.ed.discard_floating()
        self.ed.unregister_handler(self)

    def on_key_press(self, k, m):
        if k == key.ENTER:
            self._stamp()
            return True

        if k in [key.SPACE, key.F3]:
            director.push(Scene(ImgSelector(self.ed.tilesdir)))

            
    def on_key_press(self, k, m):
    
        if k == key.PAGEUP or k == key.PAGEDOWN:
            if k == key.PAGEUP:
                direction = 1
            elif k == key.PAGEDOWN:
                direction = -1

            if self.ed.floating_sprite:
                    # CTRL or COMMAND -> rotate
                if (m & key.MOD_ACCEL):
                    self.ed.rotate_floating(direction)

                    # SHIFT -> opacity
                elif (m & key.MOD_SHIFT):
                    self.ed.change_floating_opacity(direction)

                    # NOTHING -> scale
                else:
                    self.ed.scale_floating(direction)
                
            return True

    def on_mouse_press(self, x, y, button, modifiers):
        self.drag_x = 0
        self.drag_y = 0
        
        if button == 1:
            self._stamp()
            return True

        elif button == 4:
            self.ed.switch_mode('edit')
            return True
        
    def on_enter(self):
        if hasattr(director, 'return_value'):
            floating = director.return_value
            sprite = NotifierSprite(floating.image,
                                    (floating.x, floating.y))

            if self.ed.sprite_grid.enabled:
                sprite.rotation = self.ed.sprite_grid.rotation
                sprite.scale = self.ed.sprite_grid.grid_scale
            
            sprite.path = floating.path
            sprite.rect = floating.rect

            self.ed.current_layer.add(sprite)
            self.ed.set_floating(sprite)


    def on_mouse_motion(self, px, py, dx, dy):
        x, y = self.ed.layers.pointer_to_world(px, py)
        if self.ed.floating_sprite:
            nx, ny= self.ed.sprite_grid.snap_to_grid((x, y))
            self.ed.move_floating(nx, ny)
        

    def on_mouse_drag(self, px, py, dx, dy, button, m):
        x, y = self.ed.layers.pointer_to_world(px, py)
        nx, ny = self.ed.sprite_grid.snap_to_grid((x, y))
        
        if self.ed.sprite_grid.enabled:
            if (nx,ny) != self.ed.floating_sprite.position:
                self.ed.floating_sprite.position = (nx, ny)
                self._stamp()
        else:
            self.ed.floating_sprite.position = (nx, ny)
            self.drag_x += dx
            self.drag_y += dy
            print self.drag_x, self.drag_y
            if self.drag_x:
                if self.drag_y == 0:
                    if self.drag_x > 0:
                        angle = 0
                    else:
                        angle = 180
                else:
                    angle = degrees(atan(self.drag_y / self.drag_x))
                
            else:
                if self.drag_y > 0:
                    angle = 90
                elif self.drag_y < 0:
                    angle = -90
                else:
                    angle = 0
            self.ed.floating_sprite.rotation = angle
            if (self.drag_x**2 + self.drag_y**2) > (1000+self.ed.floating_sprite.width*2/3)**2:
                self.drag_x = 0
                self.drag_y = 0
                self._stamp()
                
    def _stamp(self):
        print "STAMP"
        s = NotifierSprite(self.ed.floating_sprite.image,
                           (self.ed.floating_sprite.x, self.ed.floating_sprite.y),
                           self.ed.floating_sprite.rotation,
                           self.ed.floating_sprite.scale,
                           self.ed.floating_sprite.opacity)
        s.path = self.ed.floating_sprite.path
        s.rect = self.ed.floating_sprite.rect
        self.ed.layer_add_node(self.ed.current_layer, s)
        self.ed.last_stamp_pos = self.ed.floating_sprite.position
        self.ed.floating_sprite = s


class StampPlugin(Plugin):
    name = 'stamp'
    
    def __init__(self, editor):
        self.ed = editor
        stamp_mode = StampMode(editor)
        editor.register_mode(stamp_mode)
        
        
        def get_active():
            'active sprite'
            if editor.floating_sprite:
                return editor.floating_sprite
            return None
        editor.console.add_mode_variable('stamp', 'active', get_active)
        

