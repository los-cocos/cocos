'''This module defines the ScrollableLayer and ScrollingManager classes.

Controlling Scrolling
---------------------

You have two options for scrolling:

1. automatically scroll the map but stop at the map edges, and
2. scroll the map an allow the edge of the map to be displayed.

The ScrollingManager has a concept of "focus" which is the pixel
position of the player's view focus (*usually* the center of the
player sprite itself, but the player may be allowed to
move the view around, or you may move it around for them to highlight
something else in the scene). The ScrollingManager is clever enough to
manage many layers and handle scaling them.

Two methods are available for setting the map focus:

**set_focus(x, y)**
  Attempt to set the focus to the pixel coordinates given. The layer(s)
  contained in the ScrollingManager are moved accordingly. If a layer
  would be moved outside of its define px_width, px_height then the
  scrolling is restricted. The resultant restricted focal point is stored
  on the ScrollingManager as manager.fx and manager.fy.

**force_focus(x, y)**
  Force setting the focus to the pixel coordinates given. The layer(s)
  contained in the ScrollingManager are moved accordingly regardless of
  whether any out-of-bounds cells would be displayed. The .fx and .fy
  attributes are still set, but they'll *always* be set to the supplied
  x and y values.
'''

from cocos.layer.base_layers import Layer
import pyglet

class ScrollableLayer(Layer):
    '''A Cocos Layer that is scrollable in a Scene.

    A layer may have a "parallax" value which is used to scale the position
    (and not the dimensions) of the view of the layer - the layer's view
    (x, y) coordinates are calculated as::

       my_view_x = parallax * passed_view_x
       my_view_y = parallax * passed_view_y

    Scrollable layers have a view which identifies the section of the layer
    currently visible.

    The scrolling is usually managed by a ScrollingManager.
    '''
    view_x, view_y = 0, 0
    view_w, view_h = 0, 0
    origin_x = origin_y = origin_z = 0

    def __init__(self, parallax=1):
        super(ScrollableLayer,self).__init__()
        self.parallax = parallax

        # force (cocos) transform anchor to be 0 so we don't OpenGL
        # glTranslate() and screw up our pixel alignment on screen
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0

        # XXX batch eh?
        self.batch = pyglet.graphics.Batch()

    def set_view(self, x, y, w, h):
        x *= self.parallax
        y *= self.parallax
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= self.origin_x
        y -= self.origin_y
        self.position = (-x, -y)

    def draw(self):
        # invoked by Cocos machinery
        super(ScrollableLayer, self).draw()

        # XXX overriding draw eh?
        pyglet.gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        pyglet.gl.glPopMatrix()

    def set_dirty(self):
        '''The viewport has changed in some way.
        '''
        pass

    is_event_handler = True
    def on_resize(self, width, height):
        self.view_w, self.view_h = width, height
        self.set_dirty()

class ScrollingManager(Layer):
    '''Manages scrolling of Layers in a Cocos Scene.

    Each ScrollableLayer that is added to this manager (via standard list
    methods) may have pixel dimensions .px_width and .px_height. Tile
    module MapLayers have these attribtues. The manager will limit scrolling
    to stay within the pixel boundary of the most limiting layer.

    If a layer has no dimensions it will scroll freely and without bound.

    The manager is initialised with the viewport (usually a Window) which has
    the pixel dimensions .width and .height which are used during focusing.

    A ScrollingManager knows how to convert pixel coordinates from its own
    pixel space to the screen space.
    '''
    def __init__(self, viewport=None):
        # initialise the viewport stuff
        if viewport is None:
            from cocos import director
            self.view_w, self.view_h = director.director.get_window_size()
        else:
            self.view_w, self.view_h = viewport.width, viewport.height

        # These variables define the Layer-space pixel view which is mapping
        # to the viewport. If the Layer is not scrolled or scaled then this
        # will be a one to one mapping.
        self.view_x, self.view_y = 0, 0

        # Focal point on the Layer
        self.fx = self.fy = 0

        super(ScrollingManager, self).__init__()

        # always transform about 0,0
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0

    is_event_handler = True
    def on_resize(self, width, height):
        self.view_w, self.view_h = width, height
        if self.children:
            self.set_focus(self.fx, self.fy)

    _scale = 0
    def set_scale(self, scale):
        self._scale = scale
        self._old_focus = None      # disable NOP check
        if self.children:
            self.set_focus(self.fx, self.fy)
    scale = property(lambda s: s._scale, set_scale)

    def add(self, child, z=0, name=None):
        '''Add the child and then update the manager's focus / viewport.
        '''
        super(ScrollingManager, self).add(child, z=z, name=name)
        # set the focus again and force it so we don't just skip because the
        # focal point hasn't changed
        self.set_focus(self.fx, self.fy, force=True)

    def pixel_from_screen(self, x, y):
        '''Look up the Layer-space pixel matching the screen-space pixel.

        Account for viewport, layer and screen transformations.
        '''
        # director display scaling
        x, y = director.get_virtual_coordinates(x, y)

        # normalise x,y coord
        ww, wh = director.get_window_size()
        sx = x / ww
        sy = y / wh

        # get the map-space dimensions
        vx, vy, w, h = self.view_x, self.view_y, self.view_w, self.view_h

        #print (int(x), int(y)), (vx, vy, w, h), int(vx + sx * w), int(vy + sy * h)

        # convert screen pixel to map pixel
        return int(vx + sx * w), int(vy + sy * h)

    def pixel_to_screen(self, x, y):
        '''Look up the screen-space pixel matching the Layer-space pixel.

        Account for viewport, layer and screen transformations.
        '''
        raise NotImplementedError('do this some day')
        # scaling of layer
        x *= self.scale
        y *= self.scale

        # XXX rotation of layer

        # shift for viewport
        x += self.view_x
        y += self.view_y

        # XXX director display scaling

        return int(x), int(y)

    _old_focus = None
    def set_focus(self, fx, fy, force=False):
        '''Determine the viewport based on a desired focus pixel in the
        Layer space (fx, fy) and honoring any bounding restrictions of
        child layers.

        The focus will always be shifted to ensure no child layers display
        out-of-bounds data, as defined by their dimensions px_width and px_height.
        '''
        # if no child specifies dimensions then just force the focus
        if not [l for z,l in self.children if hasattr(l, 'px_width')]:
            return self.force_focus(fx, fy)

        # This calculation takes into account the scaling of this Layer (and
        # therefore also its children).
        # The result is that all chilren will have their viewport set, defining
        # which of their pixels should be visible.

        fx, fy = int(fx), int(fy)

        a = (fx, fy, self.scale)

        # check for NOOP (same arg passed in)
        if not force and self._old_focus == a:
            return
        self._old_focus = a

        # collate children dimensions
        x1 = []; y1 = []; x2 = []; y2 = []
        for z, layer in self.children:
            if not hasattr(layer, 'px_width'): continue
            x1.append(layer.origin_x)
            y1.append(layer.origin_y)
            x2.append(layer.origin_x + layer.px_width)
            y2.append(layer.origin_y + layer.px_height)

        # figure the child layer min/max bounds
        b_min_x = min(x1)
        b_min_y = min(y1)
        b_max_x = min(x2)
        b_max_y = min(y2)

        # get our viewport information, scaled as appropriate
        w = int(self.view_w / self.scale)
        h = int(self.view_h / self.scale)
        w2, h2 = w//2, h//2

        # check for the minimum, and then maximum bound
        if (fx - w2) < b_min_x:
            fx = b_min_x + w2       # hit minimum X extent
        elif (fx + w2) > b_max_x:
            fx = b_max_x - w2       # hit maximum X extent
        if (fy - h2) < b_min_y:
            fy = b_min_y + h2       # hit minimum Y extent
        elif (fy + h2) > b_max_y:
            fy = b_max_y - h2       # hit maximum Y extent

        # ... and this is our focus point, center of screen
        self.fx, self.fy = map(int, (fx, fy))

        # determine child view bounds to match that focus point
        x, y = int(fx - w2), int(fy - h2)
        self.view_x, self.view_y = x, y
        for z, layer in self.children:
            layer.set_view(x, y, w, h)

    def force_focus(self, fx, fy):
        '''Force the manager to focus on a point, regardless of any managed layer
        visible boundaries.

        '''
        # This calculation takes into account the scaling of this Layer (and
        # therefore also its children).
        # The result is that all chilren will have their viewport set, defining
        # which of their pixels should be visible.

        self.fx, self.fy = map(int, (fx, fy))

        # get our scaled view size
        w = int(self.view_w / self.scale)
        h = int(self.view_h / self.scale)
        cx, cy = w//2, h//2

        # bottom-left corner of the
        x, y = fx - cx * self.scale, fy - cy * self.scale

        self.view_x, self.view_y = x, y

        # translate the layers to match focus
        for z, layer in self.children:
            layer.set_view(x, y, w, h)

