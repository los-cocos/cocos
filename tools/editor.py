'''Cocos tilemap editor!

Usage: editor.py <level.xml>

The level must contain at least one <rectmap> and one <tileset> (either
directly or via <requires>).

PALETTE:
- Click LMB in the palette to select the active tile.
- Use LMB dragging on the palette to drag it around the window.

MAP:
- Click LMB in the map to set the map to the active tile.
- Click RMB in the map to clear the map cell.
- Use the scroll-wheel to zoom in and out.
- Use LMB dragging to pan around the map. Alternatively use the arrow keys
  to pan around.

Hit "d" to turn some debugging information on (cell location, pixel location,
cell properties).

Hit control-s to save the map and quit.

Hit control-q, or escape, or the window close button to quit without saving.

'''

from __future__ import division, print_function, unicode_literals

import pyglet
from pyglet.gl import *
import cocos
from cocos.director import director

class TileEditorLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, manager, level_to_edit, selector, filename):
        super(TileEditorLayer, self).__init__()
        self.manager = manager
        self.level_to_edit = level_to_edit
        self.filename = filename
        self.highlight = None
        self.selector = selector
        self.tileset = selector.tileset

    def on_key_press(self, key, modifier):
        if modifier & pyglet.window.key.MOD_ACCEL:
            if key == pyglet.window.key.S:
                self.level_to_edit.save_xml(self.filename)
                director.pop()
            elif key == pyglet.window.key.Q:
                director.pop()
        if key == pyglet.window.key.D:
            m = self.selector.map_layer
            m.set_debug(not m.debug)

    _desired_scale = 1
    def on_mouse_scroll(self, x, y, dx, dy):
        if dy < 0:
            if self._desired_scale < .2: return True
            self._desired_scale -= .1
        elif dy > 0:
            if self._desired_scale > 2: return True
            self._desired_scale += .1
        if dy:
            self.manager.do(cocos.actions.ScaleTo(self._desired_scale, .1))
            return True

    def on_text_motion(self, motion):
        fx, fy = self.manager.fx, self.manager.fy
        if motion == pyglet.window.key.MOTION_UP:
            self.manager.set_focus(fx, fy+64/self._desired_scale)
        elif motion == pyglet.window.key.MOTION_DOWN:
            self.manager.set_focus(fx, fy-64/self._desired_scale)
        elif motion == pyglet.window.key.MOTION_LEFT:
            self.manager.set_focus(fx-64/self._desired_scale, fy)
        elif motion == pyglet.window.key.MOTION_RIGHT:
            self.manager.set_focus(fx+64/self._desired_scale, fy)
        else:
            return False
        return True

    _dragging = False
    def on_mouse_press(self, x, y, buttons, modifiers):
        self._drag_start = (x, y)
        self._dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not buttons & pyglet.window.mouse.LEFT:
            return False
        if not self._dragging:
            _x, _y = self._drag_start
            if abs(x - _x) + abs(y - _y) < 6:
                return False
        self._dragging = True
        self.manager.set_focus(self.manager.fx-dx/self._desired_scale,
            self.manager.fy-dy/self._desired_scale)

    def on_mouse_release(self, x, y, buttons, modifiers):
        if self._dragging:
            self._dragging = False
            return False
        m = self.selector.map_layer

        # get the cell and cell coordinate
        x, y = self.manager.pixel_from_screen(x, y)
        cell = m.get_at_pixel(x, y)
        if not cell:
            # click not in map
            return

        # now add the cell
        if buttons & pyglet.window.mouse.LEFT:
            cell.tile = self.selector.tileset[self.selector.current.tile_id]
            self.selector.map_layer.set_dirty()
        elif buttons & pyglet.window.mouse.RIGHT:
            cell.tile = None
            self.selector.map_layer.set_dirty()
        return True

    def on_mouse_motion(self, x, y, dx, dy):
        m = self.selector.map_layer
        cell = m.get_at_pixel(*self.manager.pixel_from_screen(x, y))
        if not cell:
            self.highlight = None
            return True
        x = cell.x + m.origin_x
        y = cell.y + m.origin_y
        self.highlight = (x, y, x+m.tw, y+m.th)
        return True

    def draw(self):
        if self.highlight is None:
            return
        glPushMatrix()
        self.transform()
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 0, .3)
        glRectf(*self.highlight)
        glPopAttrib()
        glPopMatrix()

class TileSetLayer(cocos.layer.Layer):
    is_event_handler = True

    TILE_SIZE = 32
    def __init__(self, level_to_edit):
        super(TileSetLayer, self).__init__()
        self.level_to_edit = level_to_edit
        self.map_layer = next(level_to_edit.find(cocos.tiles.MapLayer))[1]
        self.tileset = next(level_to_edit.findall(cocos.tiles.TileSet))[1]
        self.batch = pyglet.graphics.Batch()

        # labels
        ly = self.TILE_SIZE * 8 + 8
        self.tiles_label = pyglet.text.Label('Tiles', batch=self.batch, y=ly)
        self.active_tab = self.tiles_label
        w = self.tiles_label.content_width + 8
        h = self.tiles_label.content_height
        self.layers_label = pyglet.text.Label('Layers', batch=self.batch, y=ly,
            color=(200, 200, 200, 255))
        self.layers_label.x = w
        h = max(h, self.layers_label.content_height)
        w += self.layers_label.content_width + 8
        self.tilesets_label = pyglet.text.Label('Tilesets', batch=self.batch,
            y=ly, color=(200, 200, 200, 255))
        self.tilesets_label.x = w
        h = max(h, self.tilesets_label.content_height)
        w += self.tilesets_label.content_width

        self._width = (int(w) // self.TILE_SIZE) * self.TILE_SIZE + 8
        if int(w) % self.TILE_SIZE: self._width += self.TILE_SIZE
        self._height = h + 16 + self.TILE_SIZE * 8

        # set up the background
        bg = pyglet.image.SolidColorImagePattern((0, 0, 0, 200))
        bg = pyglet.image.create(self._width, self._height, pattern=bg)

        # set up the tiles
        self.active_batch = self.tiles_batch = pyglet.graphics.Batch()
        self.bg = pyglet.sprite.Sprite(bg, group=pyglet.graphics.OrderedGroup(0),
            batch=self.active_batch)
        self.tile_sprites = []
        x = y = 4
        for n, k in enumerate(self.tileset):
            s = pyglet.sprite.Sprite(self.tileset[k].image, y=y, x=x,
                batch=self.tiles_batch)
            if not n:
                self.current = s
            s.tile_id = k
            self.tile_sprites.append(s)
            s.scale = self.TILE_SIZE / s.width
            if not n % 8:
                y = 4; x += self.TILE_SIZE
            else:
                y += self.TILE_SIZE

        # set up the layers buttons
        self.layers_batch = pyglet.graphics.Batch()
        self.layer_labels = []
        self.layer_visible = []
        y = 4
        for k,v in level_to_edit.find(cocos.tiles.MapLayer):
            l = pyglet.text.Label(k, batch=self.layers_batch, y=y,
                    color=(255,255,255,255))
            v.map_layer = l
            if v is self.map_layer:
                l.color = (255, 255, 200, 255)
            y += l.content_height + 2
            self.layer_labels.append(l)

        # set up the tilesets buttons
        self.tilesets_batch = pyglet.graphics.Batch()
        self.layer_labels = []
        y = 4
        for id, ts in self.level_to_edit.findall(cocos.tiles.TileSet):
            if id is None: id = '[no id]'
            l = pyglet.text.Label(id, batch=self.tilesets_batch,
                    color=(255,255,255,255), y=y, x=4)
            l._tileset = ts
            y += l.content_height + 2
            self.layer_labels.append(l)

        self.highlight = (4, 4)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not buttons & pyglet.window.mouse.LEFT:
            return False
        if self._drag_start is None:
            return False
        if not self._dragging:
            _x, _y = self._drag_start
            if abs(x - _x) + abs(y - _y) < 6:
                return False
        self._dragging = True
        x, y = self.position
        self.position = (x+dx, y+dy)
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        if self._dragging:
            self._dragging = False
            self._drag_start = None
            return True

        lx, ly = self.position

        if self.active_tab is self.tiles_label:
            for s in self.tile_sprites:
                sx = s.x + lx
                sy = s.y + ly
                if x < sx or x > sx + s.width: continue
                if y < sy or y > sy + s.height: continue
                self.current = s
                self.highlight = (s.x, s.y)
                return True
        #elif self.active_tab is self.layers_label:
            #XXX handle clicks in there...

        _x = self.tiles_label.x+lx
        _y = self.tiles_label.y+ly
        if (x > _x and x < _x + self.tiles_label.content_width and
                y > _y and y < _y + self.tiles_label.content_height):
            self.active_tab.color = (200, 200, 200, 255)
            self.active_tab = self.tiles_label
            self.active_tab.color = (255, 255, 255, 255)
            self.active_batch = self.tiles_batch
            return True

        _x = self.layers_label.x+lx
        _y = self.layers_label.y+ly
        if (x > _x and x < _x + self.layers_label.content_width and
                y > _y and y < _y + self.layers_label.content_height):
            self.active_tab.color = (200, 200, 200, 255)
            self.active_tab = self.layers_label
            self.active_tab.color = (255, 255, 255, 255)
            self.active_batch = self.layers_batch
            return True

        _x = self.tilesets_label.x+lx
        _y = self.tilesets_label.y+ly
        if (x > _x and x < _x + self.tilesets_label.content_width and
                y > _y and y < _y + self.tilesets_label.content_height):
            self.active_tab.color = (200, 200, 200, 255)
            self.active_tab = self.tilesets_label
            self.active_tab.color = (255, 255, 255, 255)
            self.active_batch = self.tilesets_batch
            return True

        sx = self.bg.x + lx
        sy = self.bg.y + ly
        if x < sx or x > sx + self.bg.width: return False
        if y < sy or y > sy + self.bg.height: return False

        #self._dragging = True
        return True

    _dragging = False
    def on_mouse_press(self, x, y, buttons, modifiers):
        lx, ly = self.position
        _x = self.bg.x+lx
        _y = self.bg.y+ly
        if (x > _x and x < _x + self.bg.width and
                y > _y and y < _y + self.bg.height):
            self._drag_start = (x, y)
        else:
            self._drag_start = None
        self._dragging = False

    def draw(self):
        self.transform()
        self.active_batch.draw()
        #self.tilesets_batch.draw()

        if self.active_batch is self.tiles_batch:
            glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1, 1, 1, .3)
            x, y = self.highlight
            glRectf(x, y, x+self.TILE_SIZE, y+self.TILE_SIZE)
            glPopAttrib()


class EditorScene(cocos.scene.Scene):

    def __init__(self, edit_level_xml):
        super(EditorScene, self).__init__()

        self.manager = cocos.layer.ScrollingManager()
        #if bg_level_xml:
            #level = cocos.tiles.load(bg_level_xml)[bg_level_id]
            #self.manager.append(level)
            #level.opacity = 100
            #self.add(level, z=0)

        level_to_edit = cocos.tiles.load(edit_level_xml)

        mz = 0
        for id, layer in level_to_edit.find(cocos.tiles.MapLayer):
            self.manager.add(layer, z=layer.origin_z)
            mz = max(layer.origin_z, mz)
        self.add(self.manager)

        s = TileSetLayer(level_to_edit)
        self.add(s, z=mz+2)

        e = TileEditorLayer(self.manager, level_to_edit, s, edit_level_xml)
        self.manager.add(e, z=mz+1)

        self.manager.set_focus(0, 0)

    def edit_complete(self, layer):
        pyglet.app.exit()

if __name__ == '__main__':
    import sys

    try:
        edit_level_xml = sys.argv[1]
    except:
        print('Usage: %s <level.xml>'%sys.argv[0])
        sys.exit(0)

    director.init(width=1024, height=768)
    #director.show_FPS = True

    pyglet.gl.glClearColor(1, 1, 1, 1)

    director.run(EditorScene(edit_level_xml))


