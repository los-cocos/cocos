#!/usr/bin/env python

'''
Tile Maps
=========

Tile maps are made of two components:

tiles
   Tiles may be stand-alone or part of a TileSet.
maps
   MapLayers are made of either rectangular or hexagonal Cells which
   reference the tiles used to draw the cell.

These may be constructed manually or loaded from XML resource files which
are used to store the specification of tile sets and tile maps. A given
resource XML file may define multiple tile sets and maps and may even
reference other external XML resource files. This would allow a single
tile set to be used by multiple tile maps.

--------------------------
The XML File Specification
--------------------------

Assuming the following XML file called "example.xml"::

    <?xml version="1.0"?>
    <resource>
      <require file="ground-tiles.xml" namespace="ground" />

      <rectmap id="level1">
       <column>
        <cell>
          <tile ref="ground:grass" />
        </cell>
        <cell>
          <tile ref="ground:house" />
          <property type="bool" name="secretobjective" value="True" />
        </cell>
       </column>
      </map>
    </resource>

You may load that resource and examine it::

  >>> r = load('example.xml')
  >>> r['level1']

XXX TBD


-----------------
XML file contents
-----------------

XML resource files must contain a document-level tag <resource>::

    <?xml version="1.0"?>
    <resource>
     ...
    </resource>

You may draw in other resource files by using the <require> tag:

    <require file="road-tiles.xml" />

This will load "road-tiles.xml" into the resource's namespace.
If you wish to avoid id clashes you may supply a namespace:

    <require file="road-tiles.xml" namespace="road" />

Other tags within <resource> are:

<image file="" id="">
    Loads file with pyglet.image.load.

<imageatlas file="" [id="" size="x,y"]>
    Sets up an image atlas for child <image> tags to use. Child tags are of
    the form:

        <image offset="" id="" [size=""]>

    If the <imageatlas> tag does not provide a size attribute then all
    child <image> tags must provide one.

<tileset id="">
    Sets up a TileSet object. Child tags are of the form:

       <tile id="">
         [<image ...>]
       </tile>

    The <image> tag is optional, this tiles may have only properties (or be
    completely empty).

<rectmap id="" tile_size="" [origin=""]>
    Sets up a RectMap object. Child tags are of the form:

       <column>
        <cell tile="" />
       </column>

Most tags may additionally have properties specified as:

   <property [type=""] name="" value="" />

Where type is one of "unicode", "int", "float" or "bool". The property will
be a unicode string by default if no type is specified.

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: resource.py 1078 2007-08-01 03:43:38Z r1chardj0n3s $'

import os
import math
import weakref
from xml.etree import ElementTree

import pyglet

import cocos
from cocos.director import director

class ResourceError(Exception):
    pass

# XXX this should use pyglet.resource to load all resources
# XXX (though how path extension works isn't clear)

class Resource(dict):
    cache = {}
    def __init__(self, filename, paths=None):
        self.filename = filename
        if paths is None:
            self.paths = []
        else:
            self.paths = paths

        self.namespaces = {}        # map local name to filename
        tree = ElementTree.parse(filename)
        root = tree.getroot()
        if root.tag != 'resource':
            raise ResourceError('document is <%s> instead of <resource>'%
                root.name)
        self.handle(root)

    def find_file(self, filename):
        if os.path.isabs(filename):
            return filename
        if os.path.exists(filename):
            return filename
        for path in self.paths:
            fn = os.path.join(path, filename)
            if os.path.exists(fn):
                return fn
        raise ResourceError('File "%s" not found in any paths'%filename)

    def resource_factory(self, tag):
        for child in tag:
            self.handle(child)

    def requires_factory(self, tag):
        filename = self.find_file(tag.get('file'))
        resource = load(filename)

        ns = tag.get('namespace')
        if ns:
            self.namespaces[ns] = resource
        else:
            # copy over all the resources from the require'd file
            # last man standing wins
            self.update(resource)

    factories = {
        'resource': resource_factory,
        'requires': requires_factory,
    }
    @classmethod
    def register_factory(cls, name):
        def decorate(func):
            cls.factories[name] = func
            return func
        return decorate

    def handle(self, tag):
        ref = tag.get('ref')
        if not ref:
            return self.factories[tag.tag](self, tag)
        return self.get_resource(ref)

    def add_resource(self, id, resource):
        self[id] = resource
    def get_resource(self, ref):
        if ':' in ref:
            ns, ref = ref.split(':', 1)
            resources = self.cache[self.namespaces[ns]]
            return resources[ref]
        return self[ref]

_cache = weakref.WeakValueDictionary()
class _NOT_LOADED(object): pass
def load(filename, paths=None):
    '''Load resource(s) defined in the indicated XML file.
    '''
    # make sure we can find files relative to this one
    dirname = os.path.dirname(filename)
    if dirname:
        if paths:
            paths = list(paths)
        else:
            paths = []
        paths.append(dirname)

    if filename in _cache:
        if _cache[filename] is _NOT_LOADED:
            raise ResourceError('Loop in XML files loading "%s"'%filename)
        return _cache[filename]

    _cache[filename] = _NOT_LOADED
    obj = Resource(filename, paths)
    _cache[filename] = obj
    return obj

#
# XML PROPERTY PARSING
#
_xml_to_python = {
    'unicode': unicode,
    'int': int,
    'float': float,
    'bool': bool,
}
_python_to_xml = {
    str: 'unicode',
    unicode: 'unicode',
    int: 'int',
    float: 'float',
    bool: 'bool',
}
def _handle_properties(tag):
    properties = {}
    for tag in tag.getiterator('property'):
        name = tag.get('name')
        type = tag.get('type') or 'unicode'
        value = tag.get('value')
        properties[name] = _xml_to_python[type](value)
    return properties

#
# IMAGE and IMAGE ATLAS
#
@Resource.register_factory('image')
def image_factory(resource, tag):
    filename = resource.find_file(tag.get('file'))
    if not filename:
        raise ResourceError('No file= on <image> tag')
    # XXX use pyglet.resource
    image = pyglet.image.load(filename)

    image.properties = _handle_properties(tag)

    if tag.get('id'):
        image.id = tag.get('id')
        resource.add_resource(image.id, image)

    return image

@Resource.register_factory('imageatlas')
def imageatlas_factory(resource, tag):
    filename = resource.find_file(tag.get('file'))
    if not filename:
        raise ResourceError('No file= on <imageatlas> tag')
    # XXX use pyglet.resource
    atlas = pyglet.image.load(filename)
    atlas.properties = _handle_properties(tag)
    if tag.get('id'):
        atlas.id = tag.get('id')
        resource.add_resource(atlas.id, atlas)

    # figure default size if specified
    if tag.get('size'):
        d_width, d_height = map(int, tag.get('size').split('x'))
    else:
        d_width = d_height = None

    for child in tag:
        if child.tag != 'image':
            raise ValueError, 'invalid child'

        if child.get('size'):
            width, height = map(int, child.get('size').split('x'))
        elif d_width is None:
            raise ValueError, 'atlas or subimage must specify size'
        else:
            width, height = d_width, d_height

        x, y = map(int, child.get('offset').split(','))
        image = atlas.get_region(x, y, width, height)
        id = child.get('id')
        resource.add_resource(id, image)
        image.properties = _handle_properties(child)

    return atlas


#
# TILE SETS
#
@Resource.register_factory('tileset')
def tileset_factory(resource, tag):
    id = tag.get('id')
    properties = _handle_properties(tag)
    tileset = TileSet(id, properties)
    resource.add_resource(tileset.id, tileset)

    for child in tag:
        id = child.get('id')
        offset = child.get('offset')
        if offset:
            offset = map(int, offset.split(','))
        else:
            offset = None
        properties = _handle_properties(child)
        image = child.find('image')
        if image is not None:
            image = resource.handle(image)
        tile = Tile(id, properties, image, offset)
        resource.add_resource(id, tile)
        tileset[id] = tile

    return tileset

class Tile(object):
    '''Tiles hold an image and some optional properties.
    '''
    def __init__(self, id, properties, image, offset=None):
        super(Tile, self).__init__()
        self.id = id
        self.properties = properties
        self.image = image
        self.offset = offset

    def __repr__(self):
        return '<%s object at 0x%x id=%r offset=%r properties=%r>'%(
            self.__class__.__name__, id(self), self.id, self.offset,
                self.properties)

class TileSet(dict):
    '''Contains a set of Tile objects referenced by some id.
    '''
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties

    # We retain a cache of opened tilesets so that multiple maps may refer to
    # the same tileset and we don't waste resources by duplicating the
    # tilesets in memory.
    tilesets = {}

    tile_id = 0
    @classmethod
    def generate_id(cls):
        cls.tile_id += 1
        return str(cls.tile_id)

    def add(self, properties, image, id=None):
        '''Add a new Tile to this TileSet, generating a unique id if
        necessary.'''
        if id is None:
            id = self.generate_id()
        self[id] = Tile(id, properties, image)


#
# RECT AND HEX MAPS
#
@Resource.register_factory('rectmap')
def rectmap_factory(resource, tag):
    width, height = map(int, tag.get('tile_size').split('x'))
    origin = tag.get('origin')
    if origin:
        origin = map(int, tag.get('origin').split(','))
    id = tag.get('id')

    # now load the columns
    cells = []
    for i, column in enumerate(tag.getiterator('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getiterator('cell')):
            tile = cell.get('tile')
            if tile: tile = resource.get_resource(tile)
            else: tile = None
            properties = _handle_properties(cell)
            c.append(RectCell(i, j, width, height, properties, tile))

    m = RectMapLayer(id, width, height, cells, origin)
    resource.add_resource(id, m)

    return m

@Resource.register_factory('hexmap')
def hexmap_factory(resource, tag):
    height = int(tag.get('tile_height'))
    width = hex_width(height)
    origin = tag.get('origin')
    if origin:
        origin = map(int, tag.get('origin').split(','))
    id = tag.get('id')

    # now load the columns
    cells = []
    for i, column in enumerate(tag.getiterator('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getiterator('cell')):
            tile = cell.get('tile')
            if tile: tile = resource.get_resource(tile)
            else: tile = None
            properties = _handle_properties(tag)
            c.append(HexCell(i, j, height, properties, tile))

    m = HexMapLayer(id, width, cells, origin)
    resource.add_resource(id, m)

    return m

def hex_width(height):
    '''Determine a regular hexagon's width given its height.
    '''
    return int(height / math.sqrt(3)) * 2

class ScrollableLayer(cocos.layer.Layer):
    '''A Cocos Layer that is scrollable in a Scene.

    The scrolling is usually managed by a ScrollingManager.
    '''
    viewport_x, viewport_y = 0, 0
    def set_viewport(self, x, y, w, h):
        self.viewport_x, self.viewport_y = x, y
        self.viewport_w, self.viewport_h = w, h

    def on_draw(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-self.viewport_x, -self.viewport_y, 0)
        super(ScrollableLayer, self).on_draw()
        pyglet.gl.glPopMatrix()

    def get_virtual_coordinates(self, x, y):
        '''Translate window-space coordinates to pixel coordinates in the
        layer's space. This will include any transformation from the
        director and viewport translation.
        '''
        x, y = director.get_virtual_coordinates(x, y)
        return x+self.viewport_x, y+self.viewport_y

class MapLayer(ScrollableLayer):
    '''Base class for Maps.

    Both rect and hex maps have the following attributes:

        id              -- identifies the map in XML and Resources
        (width, height) -- size of map in cells
        (px_width, px_height)      -- size of map in pixels
        (tw, th)        -- size of each cell in pixels
        (x, y, z)       -- offset of map top left from origin in pixels
        cells           -- array [x][y] of Cell instances
    '''
    def __init__(self):
        self._sprites = {}
        super(MapLayer, self).__init__()

    def set_dirty(self):
        '''Force re-calculation of the sprites to draw for the viewport.
        '''
        self._sprites.clear()

    def set_viewport(self, x, y, w, h):
        super(MapLayer, self).set_viewport(x, y, w, h)

        # update the sprites set
        keep = set()
        for cell in self.get_in_region(x, y, x+w, y+h):
            cx, cy = key = cell.origin[:2]
            keep.add(key)
            if key not in self._sprites and cell.tile is not None:
                self._sprites[key] = pyglet.sprite.Sprite(cell.tile.image,
                    x=cx, y=cy, batch=self.batch)
        for k in list(self._sprites):
            if k not in keep:
                del self._sprites[k]

class RegularTesselationMapLayer(MapLayer):
    '''A class of MapLayer that has a regular array of Cells.
    '''
    def get_cell(self, x, y):
        ''' Return Cell at cell pos=(x,y).

        Return None if out of bounds.'''
        if x < 0 or y < 0:
            return None
        try:
            return self.cells[x][y]
        except IndexError:
            return None

class RectMapLayer(RegularTesselationMapLayer):
    '''Rectangular map.

    Cells are stored in column-major order with y increasing up,
    allowing [x][y] addressing:
    +---+---+---+
    | d | e | f |
    +---+---+---+
    | a | b | c |
    +---+---+---+
    Thus cells = [['a', 'd'], ['b', 'e'], ['c', 'f']]
    and cells[0][1] = 'd'
    '''
    def __init__(self, id, tw, th, cells, origin=None):
        super(RectMapLayer, self).__init__()
        self.id = id
        self.tw, self.th = tw, th
        if origin is None:
            origin = (0, 0, 0)
        self.x, self.y, self.z = origin
        self.cells = cells
        self.px_width = len(cells) * tw
        self.px_height = len(cells[0]) * th

    def save_xml(self, tilesets):
        #filename = raw_input('filename for save? > ')
        #if not filename.strip():
        #    print 'Filename blank - save skipped'
        #    return
        filename = 'editor-save.xml'

        # generate the XML
        root = ElementTree.Element('resource')
        for fn, namespace in tilesets:
            r = ElementTree.SubElement(root, 'requires', file=fn)
            if namespace:
                r.set('namespace', namespace)
        m = ElementTree.SubElement(root, 'rectmap', id=self.id,
            tile_size='%dx%d'%(self.tw, self.th),
            origin='%s,%s,%s'%(self.x, self.y, self.z))
        for column in self.cells:
            c = ElementTree.SubElement(m, 'column')
            for cell in column:
                cell._as_xml(c)
        tree = ElementTree.ElementTree(root)
        tree.write(filename)

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        '''
        x1 = max(0, x1 // self.tw)
        y1 = max(0, y1 // self.th)
        x2 = min(len(self.cells), x2 // self.tw + 1)
        y2 = min(len(self.cells[0]), y2 // self.th + 1)
        return [self.cells[x][y] for x in range(int(x1), int(x2)) for y in range(int(y1), int(y2))]

    def get(self, x, y):
        ''' Return Cell at pixel px=(x,y).

        Return None if out of bounds.'''
        return self.get_cell(int(x // self.tw), int(y // self.th))

    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    def get_neighbor(self, cell, direction):
        '''Get the neighbor Cell in the given direction (dx, dy) which
        is one of self.UP, self.DOWN, self.LEFT or self.RIGHT.

        Returns None if out of bounds.
        '''
        dx, dy = direction
        return self.get_cell(cell.x + dx, cell.y + dy)


class Cell(object):
    '''Base class for cells from rect and hex maps.

    Common attributes:
        x, y            -- top-left coordinate
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells
    '''
    def __init__(self, x, y, width, height, properties, tile):
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.properties = properties
        self.tile = tile

    def _as_xml(self, parent):
        c = ElementTree.SubElement(parent, 'cell')
        if self.tile:
            c.set('tile', self.tile.id)
        for k in self.properties:
            v = self.properties[k]
            ElementTree.SubElement(c, 'property', value=v,
                type=_python_to_xml[type(v)])

    def __repr__(self):
        return '<%s object at 0x%x (%g, %g) properties=%r tile=%r>'%(
            self.__class__.__name__, id(self), self.x, self.y,
                self.properties, self.tile)

class RectCell(Cell):
    '''A rectangular cell from a MapLayer.

    Read-only attributes:
        top         -- y extent
        bottom      -- y extent
        left        -- x extent
        right       -- x extent
        origin      -- (x, y) of bottom-left corner
        center      -- (x, y)
        topleft     -- (x, y) of top-left corner
        topright    -- (x, y) of top-right corner
        bottomleft  -- (x, y) of bottom-left corner
        bottomright -- (x, y) of bottom-right corner
        midtop      -- (x, y) of middle of top side
        midbottom   -- (x, y) of middle of bottom side
        midleft     -- (x, y) of middle of left side
        midright    -- (x, y) of middle of right side
    '''
    def get_origin(self):
        return self.x * self.width, self.y * self.height
    origin = property(get_origin)

    # ro, side in pixels, y extent
    def get_top(self):
        return (self.y + 1) * self.height
    top = property(get_top)

    # ro, side in pixels, y extent
    def get_bottom(self):
        return self.y * self.height
    bottom = property(get_bottom)

    # ro, in pixels, (x, y)
    def get_center(self):
        return (self.x * self.width + self.width // 2,
            self.y * self.height + self.height // 2)
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        return (self.x * self.width + self.width // 2,
            (self.y + 1) * self.height)
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        return (self.x * self.width + self.width // 2, self.y * self.height)
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        return self.x * self.width
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        return (self.x + 1) * self.width
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        return (self.x * self.width, (self.y + 1) * self.height)
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        return ((self.x + 1) * self.width, (self.y + 1) * self.height)
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        return (self.x * self.height, self.y * self.height)
    bottomleft = property(get_bottomleft)
    origin = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        return ((self.x + 1) * self.width, self.y * self.height)
    bottomright = property(get_bottomright)

    # ro, mid-point in pixels, (x, y)
    def get_midleft(self):
        return (self.x * self.width, self.y * self.height + self.height // 2)
    midleft = property(get_midleft)

    # ro, mid-point in pixels, (x, y)
    def get_midright(self):
        return ((self.x + 1) * self.width,
            self.y * self.height + self.height // 2)
    midright = property(get_midright)


class HexMapLayer(RegularTesselationMapLayer):
    '''MapLayer with flat-top, regular hexagonal cells.

    Additional attributes extending MapBase:

        edge_length -- length of an edge in pixels

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map:
          /d\ /h\
        /b\_/f\_/
        \_/c\_/g\
        /a\_/e\_/
        \_/ \_/
    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
    '''
    def __init__(self, id, th, cells, origin=None):
        super(HexMapLayer, self).__init__()
        self.id = id
        self.th = th
        if origin is None:
            origin = (0, 0, 0)
        self.x, self.y, self.z = origin
        self.cells = cells

        # figure some convenience values
        s = self.edge_length = int(th / math.sqrt(3))
        self.tw = self.edge_length * 2

        # now figure map dimensions
        width = len(cells); height = len(cells[0])
        self.px_width = self.tw + (width - 1) * (s + s // 2)
        self.px_height = height * self.th
        if not width % 2:
            self.px_height += (th // 2)

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the pixel bounds
        specified by the bottom-left (x1, y1) and top-right (x2, y2) corners.
        '''
        col_width = self.tw // 2 + self.tw // 4
        x1 = max(0, x1 // col_width)
        y1 = max(0, y1 // self.th - 1)
        x2 = min(len(self.cells), x2 // col_width + 1)
        y2 = min(len(self.cells[0]), y2 // self.th + 1)
        return [self.cells[x][y] for x in range(x1, x2) for y in range(y1, y2)]

    def get(self, x, y):
        '''Get the Cell at pixel px=(x,y).
        Return None if out of bounds.'''
        s = self.edge_length
        # map is divided into columns of
        # s/2 (shared), s, s/2(shared), s, s/2 (shared), ...
        x = x // (s/2 + s)
        if x % 2:
            # every second cell is up one
            y -= self.th // 2
        y = y // self.th
        return self.get_cell(x, y)

    UP = 'up'
    DOWN = 'down'
    UP_LEFT = 'up left'
    UP_RIGHT = 'up right'
    DOWN_LEFT = 'down left'
    DOWN_RIGHT = 'down right'
    def get_neighbor(self, cell, direction):
        '''Get the neighbor HexCell in the given direction which
        is one of self.UP, self.DOWN, self.UP_LEFT, self.UP_RIGHT,
        self.DOWN_LEFT or self.DOWN_RIGHT.

        Return None if out of bounds.
        '''
        if direction is self.UP:
            return self.get_cell(cell.x, cell.y + 1)
        elif direction is self.DOWN:
            return self.get_cell(cell.x, cell.y - 1)
        elif direction is self.UP_LEFT:
            if cell.x % 2:
                return self.get_cell(cell.x - 1, cell.y + 1)
            else:
                return self.get_cell(cell.x - 1, cell.y)
        elif direction is self.UP_RIGHT:
            if cell.x % 2:
                return self.get_cell(cell.x + 1, cell.y + 1)
            else:
                return self.get_cell(cell.x + 1, cell.y)
        elif direction is self.DOWN_LEFT:
            if cell.x % 2:
                return self.get_cell(cell.x - 1, cell.y)
            else:
                return self.get_cell(cell.x - 1, cell.y - 1)
        elif direction is self.DOWN_RIGHT:
            if cell.x % 2:
                return self.get_cell(cell.x + 1, cell.y)
            else:
                return self.get_cell(cell.x + 1, cell.y - 1)
        else:
            raise ValueError, 'Unknown direction %r'%direction

# Note that we always add below (not subtract) so that we can try to
# avoid accumulation errors due to rounding ints. We do this so
# we can each point at the same position as a neighbor's corresponding
# point.
class HexCell(Cell):
    '''A flat-top, regular hexagon cell from a HexMap.

    Read-only attributes:
        top             -- y extent
        bottom          -- y extent
        left            -- (x, y) of left corner
        right           -- (x, y) of right corner
        center          -- (x, y)
        origin          -- (x, y) of bottom-left corner of bounding rect
        topleft         -- (x, y) of top-left corner
        topright        -- (x, y) of top-right corner
        bottomleft      -- (x, y) of bottom-left corner
        bottomright     -- (x, y) of bottom-right corner
        midtop          -- (x, y) of middle of top side
        midbottom       -- (x, y) of middle of bottom side
        midtopleft      -- (x, y) of middle of left side
        midtopright     -- (x, y) of middle of right side
        midbottomleft   -- (x, y) of middle of left side
        midbottomright  -- (x, y) of middle of right side
    '''
    def __init__(self, x, y, height, properties, tile):
        width = hex_width(height)
        Cell.__init__(self, x, y, width, height, properties, tile)

    def get_origin(self):
        x = self.x * (self.width / 2 + self.width // 4)
        y = self.y * self.height
        if self.x % 2:
            y += self.height // 2
        return (x, y)
    origin = property(get_origin)

    # ro, side in pixels, y extent
    def get_top(self):
        y = self.get_origin()[1]
        return y + self.height
    top = property(get_top)

    # ro, side in pixels, y extent
    def get_bottom(self):
        return self.get_origin()[1]
    bottom = property(get_bottom)

    # ro, in pixels, (x, y)
    def get_center(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y + self.height // 2)
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y + self.height)
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y)
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        x, y = self.get_origin()
        return (x, y + self.height // 2)
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        x, y = self.get_origin()
        return (x + self.width, y + self.height // 2)
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        x, y = self.get_origin()
        return (x + self.width // 4, y + self.height)
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4, y + self.height)
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        x, y = self.get_origin()
        return (x + self.width // 4, y)
    bottomleft = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4, y)
    bottomright = property(get_bottomright)

    # ro, middle of side in pixels, (x, y)
    def get_midtopleft(self):
        x, y = self.get_origin()
        return (x + self.width // 8, y + self.height // 2 + self.height // 4)
    midtopleft = property(get_midtopleft)

    # ro, middle of side in pixels, (x, y)
    def get_midtopright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4 + self.width // 8,
            y + self.height // 2 + self.height // 4)
    midtopright = property(get_midtopright)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomleft(self):
        x, y = self.get_origin()
        return (x + self.width // 8, y + self.height // 4)
    midbottomleft = property(get_midbottomleft)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4 + self.width // 8,
            y + self.height // 4)
    midbottomright = property(get_midbottomright)


#
# SCROLLING MANAGEMENT
#
class ScrollingManager(list):
    '''Manages scrolling of Layers in a Cocos Scene.

    Each layer that is added to this manager (via standard list methods)
    may have pixel dimensions .px_width and .px_height. MapLayers have these
    attribtues. The manager will limit scrolling to stay within the pixel
    boundary of the most limiting layer.

    If a layer has no dimensions it will scroll freely and without bound.

    The manager is initialised with the viewport (usually a Window) which has
    the pixel dimensions .width and .height which are used during focusing.
    '''
    def __init__(self, viewport):
        self.viewport = viewport
        self.fx = self.fy = 0

    def append(self, item):
        super(ScrollingManager, self).append(item)
        item.set_viewport(0, 0, self.viewport.width, self.viewport.height)

    def set_focus(self, fx, fy):
        '''Determine the focal point of the view based on focus (fx, fy),
        and registered layers.

        The focus will always be
        '''
        # enforce int-only positioning of focus
        fx = int(fx)
        fy = int(fy)

        # check that any layer has bounds
        bounded = []
        for layer in self:
            if hasattr(layer, 'px_width'):
                bounded.append(layer)
        if not bounded:
            return (fx, fy)

        # figure the bounds min/max
        m = bounded[0]
        b_min_x = m.x
        b_min_y = m.y
        b_max_x = m.x + m.px_width
        b_max_y = m.y + m.px_height
        for m in bounded[1:]:
            b_min_x = min(b_min_x, m.x)
            b_min_y = min(b_min_y, m.y)
            b_max_x = min(b_max_x, m.x + m.px_width)
            b_max_y = min(b_max_y, m.y + m.px_height)

        # figure the view min/max based on focus
        w2 = self.viewport.width/2
        h2 = self.viewport.height/2

        # check for the minimum bound
        v_min_x = fx - w2
        v_min_y = fy - h2
        x_moved = y_moved = False
        if v_min_x < b_min_x:
            fx += b_min_x - v_min_x
            x_moved = True
        if v_min_y < b_min_y:
            fy += b_min_y - v_min_y
            y_moved = True

        # now check the maximum bound - only if we've not already hit a bound
        v_max_x = fx + w2
        v_max_y = fy + h2
        if not x_moved and v_max_x > b_max_x:
            fx -= v_max_x - b_max_x
        if not y_moved and v_max_y > b_max_y:
            fy -= v_max_y - b_max_y

        self.fx, self.fy = map(int, (fx, fy))

        # translate the layers to match focus
        vx, vy = self.fx - w2, self.fy - h2
        for layer in self:
            layer.set_viewport(vx, vy,
                self.viewport.width, self.viewport.height)

    def force_focus(self, fx, fy):
        self.fx, self.fy = map(int, (fx, fy))

        w2 = self.viewport.width/2
        h2 = self.viewport.height/2
        vx, vy = self.fx - w2, self.fy - h2

        # translate the layers to match focus
        for layer in self:
            layer.set_viewport(vx, vy,
                self.viewport.width, self.viewport.height)

