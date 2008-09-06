#!/usr/bin/env python

'''
Tile Maps
=========

Tile maps are made of three components:

images
   Images are from individual files for from image atlases in a single file.
tiles
   Tiles may be stand-alone or part of a TileSet.
maps
   MapLayers are made of either rectangular or hexagonal Cells which
   reference the tiles used to draw the cell.

The intent is that you may have a tile set defined in one XML file
which is shared amongst many map files (or indeed within a single
XML file). Images may be shared amongst multiple tiles with the tiles
adding different meta-data in each case.

These may be constructed manually or loaded from XML resource files which
are used to store the specification of tile sets and tile maps. A given
resource XML file may define multiple tile sets and maps and may even
reference other external XML resource files. This would allow a single
tile set to be used by multiple tile maps.


Tile Maps
---------

The RectMapLayer class extends the regular Cocos layer to handle a
regular grid of tile images, or Cells. The map layer may be manipulated
like any other Cocos layer. It also provides methods for interrogating
the map contents to find cells (eg. under the mouse) or neighboring
cells (up, down, left, right.)

Maps may be defined in Python code, but it is a little easier to do so
in XML. To support map editing the maps support round-tripping to XML.


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

and then, assuming that level1 is a map::

  >>> scene = cocos.scene.Scene(r['level1'])

if you wish for the level to scroll, you use the ScrollingManager::

  >>> manager = tiles.ScrollingManager()
  >>> manager.append(r['level1']

and later set the focus with::

  >>> manager.set_focus(focus_x, focus_y)

Typically the focus is set to the center of the player's sprite. The
focusing will honor any tile map boundaries and prevent area outside
those boundaries from being displayed.

If you are only scrolling layers with sprites in them (ie. regular
Cocos Layers, not RectMapLayers) then there are no boundaries and
the map will scroll without bound in any direction.

If you wish you may force the focus to display areas outside your
tile maps you may use the ``force_focus`` method of ScrollingManager.


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

If a namespace is given then the element ids from the "road-tiles.xml"
will be prefixed by the namespace and a period, e.g. "road.bitumen".

Other tags within <resource> are:

<image file="" id="">
    Loads file with pyglet.image.load and gives it the id which is used
    by tiles to reference the image.

<imageatlas file="" [id="" size="x,y"]>
    Sets up an image atlas for child <image> tags to use. Child tags are of
    the form:

        <image offset="" id="" [size=""]>

    If the <imageatlas> tag does not provide a size attribute then all
    child <image> tags must provide one. Image atlas ids are optional as
    they are currently not reference directly.

<tileset id="">
    Sets up a TileSet object. Child tags are of the form:

       <tile id="">
         [<image ...>]
       </tile>

    The <image> tag is optional; these tiles may have only properties (or be
    completely empty). The id is used by maps to reference the tile.

<rectmap id="" tile_size="" [origin=""]>
    Sets up a RectMap object. Child tags are of the form:

       <column>
        <cell tile="" />
       </column>

Most tags may additionally have properties specified as:

   <property [type=""] name="" value="" />

Where type is one of "unicode", "int", "float" or "bool". The property will
be a unicode string by default if no type is specified. The properties
are loaded into a dictionary called ".properties" on the appropriate
Image, Tile, Map and Cell instance.
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

class Resource(object):
    '''Load some tile mapping resources from an XML file.
    '''
    cache = {}
    def __init__(self, filename, paths=None):
        self.filename = filename
        if paths is None:
            self.paths = []
        else:
            self.paths = paths

        # id to map, tileset, etc.
        self.contents = {}

        # list of (namespace, Resource) from <requires> tags
        self.requires = []

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
        self.requires.append((tag.get('namespace', ''), resource))

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

    def __contains__(self, ref):
        return ref in self.contents

    def __getitem__(self, ref):
        reqns = ''
        id = ref
        if ':' in ref:
            reqns, id = ref.split(':', 1)
        elif id in self.contents:
            return self.contents[id]
        for ns, res in self.requires:
            if ns != reqns: continue
            if id in res: return res[id]
        raise KeyError(id)

    def find(self, cls):
        '''Find all elements of the given class in this resource.
        '''
        for k in self.contents:
            if isinstance(self.contents[k], cls):
                yield (k, self.contents[k])

    def findall(self, cls, ns=''):
        '''Find all elements of the given class in this resource and all
        <require>'ed resources.
        '''
        for k in self.contents:
            if isinstance(self.contents[k], cls):
                if ns:
                    yield (ns + ':' + k, self.contents[k])
                else:
                    yield (k, self.contents[k])
        for ns, res in self.requires:
            for item in res.findall(cls, ns):
                yield item

    def add_resource(self, id, resource):
        self.contents[id] = resource
    def get_resource(self, ref):
        return self[ref]

    def save_xml(self, filename):
        '''Save this resource's XML to the indicated file.
        '''
        # generate the XML
        root = ElementTree.Element('resource')
        for namespace, res in self.requires:
            r = ElementTree.SubElement(root, 'requires', file=res.filename)
            r.tail = '\n'
            if namespace:
                r.set('namespace', namespace)
        for element in self.contents.values():
            element._as_xml(root)
        tree = ElementTree.ElementTree(root)
        tree.write(filename)

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
_xml_to_python = dict(
    unicode=unicode,
    int=int,
    float=float,
    bool=lambda value: value != "False",
)
_python_to_xml = {
    str: unicode,
    unicode: unicode,
    int: repr,
    float: repr,
    bool: repr,
}
_xml_type = {
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

    tile_id = 0
    @classmethod
    def generate_id(cls):
        cls.tile_id += 1
        return str(cls.tile_id)

    def add(self, properties, image, id=None):
        '''Add a new Tile to this TileSet, generating a unique id if
        necessary.

        Returns the Tile instance.
        '''
        if id is None:
            id = self.generate_id()
        self[id] = Tile(id, properties, image)
        return self[id]


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

    Scrollable layers have a view which identifies the section of the layer
    currently visible.

    The scrolling is usually managed by a ScrollingManager.
    '''
    view_x, view_y = 0, 0
    view_w, view_h = 0, 0
    origin_x = origin_y = origin_z = 0

    def __init__(self):
        super(ScrollableLayer,self).__init__()
        self.batch = pyglet.graphics.Batch()

    def set_view(self, x, y, w, h):
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= self.origin_x
        y -= self.origin_y
        self.position = (-x, -y)

    def draw(self):
        # invoked by Cocos machinery
        super(ScrollableLayer, self).draw()
        pyglet.gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        pyglet.gl.glPopMatrix()

class MapLayer(ScrollableLayer):
    '''Base class for Maps.

    Maps are comprised of tiles and can figure out which tiles are required to
    be rendered on screen.

    Both rect and hex maps have the following attributes:

        id              -- identifies the map in XML and Resources
        (width, height) -- size of map in cells
        (px_width, px_height)      -- size of map in pixels
        (tw, th)        -- size of each cell in pixels
        (origin_x, origin_y, origin_z)  -- offset of map top left from origin in pixels
        cells           -- array [i][j] of Cell instances
        debug           -- display debugging information on cells

    The debug flag turns on textual display of data about each visible cell
    including its cell index, origin pixel and any properties set on the cell.
    '''
    def __init__(self):
        self._sprites = {}
        super(MapLayer, self).__init__()

    def set_dirty(self):
        # re-calculate the sprites to draw for the view
        self._sprites.clear()
        self._update_sprite_set()

    def set_view(self, x, y, w, h):
        # invoked by ScrollingManager.set_focus()
        super(MapLayer, self).set_view(x, y, w, h)
        self._update_sprite_set()

    def get_visible_cells(self):
        '''Given the current view in map-space pixels, transform it based
        on the current screen-space transform and figure the region of
        map-space pixels currently visible.

        Pass to get_in_region to return a list of Cell instances.
        '''
        # XXX refactor me away
        x, y = self.view_x, self.view_y
        w, h = self.view_w, self.view_h
        return self.get_in_region(x, y, x + w, y + h)

    debug = False
    def set_debug(self, debug):
        self.debug = debug
        self._update_sprite_set()

    def _update_sprite_set(self):
        # update the sprites set
        keep = set()
        for cell in self.get_visible_cells():
            cx, cy = key = cell.origin[:2]
            keep.add(key)
            if key not in self._sprites and cell.tile is not None:
                self._sprites[key] = pyglet.sprite.Sprite(cell.tile.image,
                    x=cx, y=cy, batch=self.batch)
            s = self._sprites[key]
            if self.debug:
                if getattr(s, '_label', None): continue
                label = [
                    'cell=%d,%d'%(cell.i, cell.j),
                    'origin=%d,%d px'%(cx, cy),
                ]
                for p in cell.properties:
                    label.append('%s=%r'%(p, cell.properties[p]))
                lx, ly = cell.topleft
                s._label = pyglet.text.Label(
                    '\n'.join(label), multiline=True, x=lx, y=ly,
                    bold=True, font_size=8, width=cell.width,
                    batch=self.batch)
            else:
                s._label = None
        for k in list(self._sprites):
            if k not in keep:
                self._sprites[k]._label = None
                del self._sprites[k]

class RegularTesselationMapLayer(MapLayer):
    '''A class of MapLayer that has a regular array of Cells.
    '''
    def get_cell(self, i, j):
        ''' Return Cell at cell pos=(i, j).

        Return None if out of bounds.'''
        if i < 0 or j < 0:
            return None
        try:
            return self.cells[i][j]
        except IndexError:
            return None

class RectMapLayer(RegularTesselationMapLayer):
    '''Rectangular map.

    Cells are stored in column-major order with y increasing up,
    allowing [i][j] addressing:
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
        self.origin_x, self.origin_y, self.origin_z = origin
        self.cells = cells
        self.px_width = len(cells) * tw
        self.px_height = len(cells[0]) * th

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the map-space
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        Return a list of Cell instances.
        '''
        ox = self.origin_x
        oy = self.origin_y
        x1 = max(0, (x1 - ox) // self.tw - 1)
        y1 = max(0, (y1 - oy) // self.th - 1)
        x2 = min(len(self.cells), (x2 - ox) // self.tw + 1)
        y2 = min(len(self.cells[0]), (y2 - oy) // self.th + 1)
        return [self.cells[i][j]
            for i in range(int(x1), int(x2))
                for j in range(int(y1), int(y2))]

    def get_at_pixel(self, x, y):
        ''' Return Cell at pixel px=(x,y) on the map.

        The pixel coordinate passed in is in the map's coordinate space,
        unmodified by screen, layer or view transformations.

        Return None if out of bounds.
        '''
        return self.get_cell(int((x - self.origin_x) // self.tw),
            int((y - self.origin_y) // self.th))

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
        return self.get_cell(cell.i + dx, cell.j + dy)

    def _as_xml(self, root):
        m = ElementTree.SubElement(root, 'rectmap', id=self.id,
            tile_size='%dx%d'%(self.tw, self.th),
            origin='%s,%s,%s'%(self.origin_x, self.origin_y, self.origin_z))
        for column in self.cells:
            c = ElementTree.SubElement(m, 'column')
            c.tail = '\n'
            for cell in column:
                cell._as_xml(c)


class Cell(object):
    '''Base class for cells from rect and hex maps.

    Common attributes:
        i, j            -- index of this cell in the map
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells
    '''
    def __init__(self, i, j, width, height, properties, tile):
        self.width, self.height = width, height
        self.i, self.j = i, j
        self.properties = properties
        self.tile = tile

    def _as_xml(self, parent):
        c = ElementTree.SubElement(parent, 'cell')
        c.tail = '\n'
        if self.tile:
            c.set('tile', self.tile.id)
        for k in self.properties:
            v = self.properties[k]
            v = _python_to_xml[type(v)](v)
            ElementTree.SubElement(c, 'property', value=v,
                type=_xml_type[type(v)])

    def __repr__(self):
        return '<%s object at 0x%x (%g, %g) properties=%r tile=%r>'%(
            self.__class__.__name__, id(self), self.i, self.j,
                self.properties, self.tile)

class RectCell(Cell):
    '''A rectangular cell from a MapLayer.

    Cell attributes:
        i, j            -- index of this cell in the map
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Read-only attributes:
        x, y        -- bottom-left pixel
        top         -- y pixel extent
        bottom      -- y pixel extent
        left        -- x pixel extent
        right       -- x pixel extent
        origin      -- (x, y) of bottom-left corner pixel
        center      -- (x, y)
        topleft     -- (x, y) of top-left corner pixel
        topright    -- (x, y) of top-right corner pixel
        bottomleft  -- (x, y) of bottom-left corner pixel
        bottomright -- (x, y) of bottom-right corner pixel
        midtop      -- (x, y) of middle of top side pixel
        midbottom   -- (x, y) of middle of bottom side pixel
        midleft     -- (x, y) of middle of left side pixel
        midright    -- (x, y) of middle of right side pixel

    Note that all pixel attributes are *not* adjusted for screen,
    view or layer transformations.
    '''
    x = property(lambda self: self.i * self.width)
    y = property(lambda self: self.j * self.height)

    def get_origin(self):
        return self.i * self.width, self.j * self.height
    origin = property(get_origin)

    # ro, side in pixels, y extent
    def get_top(self):
        return (self.j + 1) * self.height
    top = property(get_top)

    # ro, side in pixels, y extent
    def get_bottom(self):
        return self.j * self.height
    bottom = property(get_bottom)

    # ro, in pixels, (x, y)
    def get_center(self):
        return (self.i * self.width + self.width // 2,
            self.j * self.height + self.height // 2)
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        return (self.i * self.width + self.width // 2,
            (self.j + 1) * self.height)
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        return (self.i * self.width + self.width // 2, self.j * self.height)
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        return self.i * self.width
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        return (self.i + 1) * self.width
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        return (self.i * self.width, (self.j + 1) * self.height)
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        return ((self.i + 1) * self.width, (self.j + 1) * self.height)
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        return (self.i * self.height, self.j * self.height)
    bottomleft = property(get_bottomleft)
    origin = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        return ((self.i + 1) * self.width, self.j * self.height)
    bottomright = property(get_bottomright)

    # ro, mid-point in pixels, (x, y)
    def get_midleft(self):
        return (self.i * self.width, self.j * self.height + self.height // 2)
    midleft = property(get_midleft)

    # ro, mid-point in pixels, (x, y)
    def get_midright(self):
        return ((self.i + 1) * self.width,
            self.j * self.height + self.height // 2)
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
        self.origin_x, self.origin_y, self.origin_z = origin
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
        return [self.cells[i][j] for i in range(x1, x2) for j in range(y1, y2)]

    # XXX add get_from_screen

    def get_at_pixel(self, x, y):
        '''Get the Cell at pixel px=(x,y).
        Return None if out of bounds.'''
        # XXX update my docstring
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
            return self.get_cell(cell.i, cell.j + 1)
        elif direction is self.DOWN:
            return self.get_cell(cell.i, cell.j - 1)
        elif direction is self.UP_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j + 1)
            else:
                return self.get_cell(cell.i - 1, cell.j)
        elif direction is self.UP_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j + 1)
            else:
                return self.get_cell(cell.i + 1, cell.j)
        elif direction is self.DOWN_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j)
            else:
                return self.get_cell(cell.i - 1, cell.j - 1)
        elif direction is self.DOWN_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j)
            else:
                return self.get_cell(cell.i + 1, cell.j - 1)
        else:
            raise ValueError, 'Unknown direction %r'%direction

# Note that we always add below (not subtract) so that we can try to
# avoid accumulation errors due to rounding ints. We do this so
# we can each point at the same position as a neighbor's corresponding
# point.
class HexCell(Cell):
    '''A flat-top, regular hexagon cell from a HexMap.

    Cell attributes:
        i, j            -- index of this cell in the map
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Read-only attributes:
        x, y            -- bottom-left pixel
        top             -- y pixel extent
        bottom          -- y pixel extent
        left            -- (x, y) of left corner pixel
        right           -- (x, y) of right corner pixel
        center          -- (x, y)
        origin          -- (x, y) of bottom-left corner of bounding rect
        topleft         -- (x, y) of top-left corner pixel
        topright        -- (x, y) of top-right corner pixel
        bottomleft      -- (x, y) of bottom-left corner pixel
        bottomright     -- (x, y) of bottom-right corner pixel
        midtop          -- (x, y) of middle of top side pixel
        midbottom       -- (x, y) of middle of bottom side pixel
        midtopleft      -- (x, y) of middle of left side pixel
        midtopright     -- (x, y) of middle of right side pixel
        midbottomleft   -- (x, y) of middle of left side pixel
        midbottomright  -- (x, y) of middle of right side pixel

    Note that all pixel attributes are *not* adjusted for screen,
    view or layer transformations.
    '''
    def __init__(self, i, j, height, properties, tile):
        width = hex_width(height)
        Cell.__init__(self, i, j, width, height, properties, tile)

    def get_origin(self):
        x = self.i * (self.width / 2 + self.width // 4)
        y = self.j * self.height
        if self.i % 2:
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
class ScrollingManager(cocos.layer.Layer):
    '''Manages scrolling of Layers in a Cocos Scene.

    Each layer that is added to this manager (via standard list methods)
    may have pixel dimensions .px_width and .px_height. MapLayers have these
    attribtues. The manager will limit scrolling to stay within the pixel
    boundary of the most limiting layer.

    If a layer has no dimensions it will scroll freely and without bound.

    The manager is initialised with the viewport (usually a Window) which has
    the pixel dimensions .width and .height which are used during focusing.

    A ScrollingManager knows how to convert pixel coordinates from its own
    pixel space to the screen space.
    '''
    def __init__(self, viewport=None):
        # initialise the viewport stuff
        if viewport is None:
            import director
            viewport = director.director.window
        self.viewport = viewport

        # These variables define the Layer-space pixel view which is mapping
        # to the viewport. If the Layer is not scrolled or scaled then this
        # will be a one to one mapping.
        self.view_x, self.view_y = 0, 0
        self.view_w, self.view_h = self.viewport.width, self.viewport.height

        # Focal point on the Layer
        self.fx = self.fy = 0

        super(ScrollingManager, self).__init__()

        # always transform about 0,0
        self.transform_anchor_x = 0
        self.transform_anchor_y = 0

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
        self.set_focus(self.fx, self.fy)

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
    def set_focus(self, fx, fy):
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
        if self._old_focus == a:
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
        w = int(self.viewport.width / self.scale)
        h = int(self.viewport.height / self.scale)
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
        self.view_w, self.view_h = w, h
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
        w = int(self.viewport.width / self.scale)
        h = int(self.viewport.height / self.scale)
        cx, cy = w//2, h//2

        # bottom-left corner of the
        x, y = fx - cx * self.scale, fy - cy * self.scale

        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h

        # translate the layers to match focus
        for z, layer in self.children:
            layer.set_view(x, y, w, h)

