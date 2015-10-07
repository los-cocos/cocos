# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
"""Tile map management and rendering.

This module provides an API for loading, saving and rendering a map
constructed of image tiles.
"""

from __future__ import division, print_function, unicode_literals
import six

__docformat__ = 'restructuredtext'
__version__ = '$Id: resource.py 1078 2007-08-01 03:43:38Z r1chardj0n3s $'

import os
from math import ceil, sqrt, floor
import struct
import weakref
from xml.etree import ElementTree

import pyglet
from pyglet import gl
import pyglet.text.formats.html as p_html

import cocos
from cocos.director import director
from cocos.rect import Rect

unicode = six.text_type


class ResourceError(Exception):
    pass


class TilesPropertyWithoutName(Exception):
    pass


class TilesPropertyWithoutValue(Exception):
    pass


class TmxUnsupportedVariant(Exception):
    pass

class Resource(object):
    """Load some tile mapping resources from an XML file.
    """
    cache = {}

    def __init__(self, filename):
        self.filename = filename

        # id to map, tileset, etc.
        self.contents = {}

        # list of (namespace, Resource) from <requires> tags
        self.requires = []

        self.path = self.find_file(filename)

    def find_file(self, filename):
        if os.path.isabs(filename):
            return filename
        if os.path.exists(filename):
            return filename
        path = pyglet.resource.location(filename).path
        return os.path.join(path, filename)

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
            if ns != reqns:
                continue
            if id in res:
                return res[id]
        raise KeyError(id)

    def find(self, cls):
        """Find all elements of the given class in this resource.
        """
        for k in self.contents:
            if isinstance(self.contents[k], cls):
                yield (k, self.contents[k])

    def findall(self, cls, ns=''):
        """Find all elements of the given class in this resource and all
        <requires>'ed resources.
        """
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
        """Save this resource's XML to the indicated file.
        """
        # generate the XML
        root = ElementTree.Element('resource')
        root.tail = '\n'
        for namespace, res in self.requires:
            r = ElementTree.SubElement(root, 'requires', file=res.filename)
            r.tail = '\n'
            if namespace:
                r.set('namespace', namespace)
        for element in self.contents.values():
            element._as_xml(root)
        tree = ElementTree.ElementTree(root)
        tree.write(filename)

    def resource_factory(self, tag):
        for child in tag:
            self.handle(child)

    def requires_factory(self, tag):
        resource = load(tag.get('file'))
        self.requires.append((tag.get('namespace', ''), resource))

    factories = {
        'resource': resource_factory,
        'requires': requires_factory,
    }


_cache = weakref.WeakValueDictionary()


class _NOT_LOADED(object):
    pass


def load(filename):
    """Load resource(s) defined in the indicated XML file.
    """
    # make sure we can find files relative to this one
    dirname = os.path.dirname(filename)
    if dirname and dirname not in pyglet.resource.path:
        if os.sep == '\\':
            # pyglet resource does not accept '\' in relative paths
            dirname = dirname.replace(os.sep, '/')
        pyglet.resource.path.append(dirname)
        pyglet.resource.reindex()

    if filename in _cache:
        if _cache[filename] is _NOT_LOADED:
            raise ResourceError('Loop in tile map files loading "%s"' % filename)
        return _cache[filename]

    _cache[filename] = _NOT_LOADED
    if filename.endswith('.tmx'):
        obj = load_tmx(filename)
    else:
        obj = load_tiles(filename)
    _cache[filename] = obj
    return obj


def load_tiles(filename):
    """Load some tile mapping resources from an XML file.
    """
    resource = Resource(filename)
    tree = ElementTree.parse(resource.path)
    root = tree.getroot()
    if root.tag != 'resource':
        raise ResourceError('document is <%s> instead of <resource>' % root.name)
    resource.handle(root)
    return resource


def decode_base64(s):
    """returns a bytes object"""
    if six.PY2:
        return s.decode('base64')
    else:
        import base64
        b = s.encode('utf-8')
        return base64.b64decode(b)


def decompress_zlib(in_bytes):
    """decompress the input array of bytes to an array of bytes using zlib"""
    if six.PY2:
        out_bytes = in_bytes.decode('zlib')
    else:
        import zlib
        out_bytes = zlib.decompress(in_bytes)
    return out_bytes


def decompress_gzip(in_bytes):
    """decompress the input array of bytes to an array of bytes using gzip"""
    import gzip
    inp = six.BytesIO(in_bytes)
    f = gzip.GzipFile(fileobj=inp)
    out_bytes = f.read()
    f.close()
    inp.close()
    return out_bytes


def load_tmx(filename):
    """Load some tile mapping resources from a TMX file.
    """
    resource = Resource(filename)

    tree = ElementTree.parse(resource.path)
    map = tree.getroot()
    if map.tag != 'map':
        raise ResourceError('document is <%s> instead of <map>' % map.name)

    width = int(map.attrib['width'])
    height = int(map.attrib['height'])

    # XXX this is ASSUMED to be consistent
    tile_width = int(map.attrib['tilewidth'])
    tile_height = int(map.attrib['tileheight'])

    tiling_style = map.attrib['orientation']

    if tiling_style == "hexagonal":
        hex_sidelenght = int(map.attrib["hexsidelength"])
        # 'x' meant hexagons with top and bottom sides parallel to x axis,
        # 'y' meant hexagons with left and right sides paralel to y axis        
        s = map.attrib["staggeraxis"]
        hex_orientation = {'x':'pointy_left', 'y':'pointy_up'}
        # 'even' or 'odd', currently cocos only displays correctly 'even'       
        lowest_columns = map.attrib["staggerindex"]=="even"
        cell_cls = HexCell  
        layer_cls = HexMapLayer
        map_height_pixels = height * tile_height + tile_height // 2

    elif tiling_style == "orthogonal":
        cell_cls = RectCell  
        layer_cls = RectMapLayer
        map_height_pixels = height * tile_height

    else:
        raise ValueError("Unsuported tiling style, must be 'orthogonal' or 'hexagonal'")

        
    # load all the tilesets
    tilesets = []
    for tag in map.findall('tileset'):
        if 'source' in tag.attrib:
            firstgid = int(tag.attrib['firstgid'])
            path = resource.find_file(tag.attrib['source'])
            with open(path) as f:
                tag = ElementTree.fromstring(f.read())
        else:
            firstgid = int(tag.attrib['firstgid'])

        name = tag.attrib['name']
        
        spacing = int(tag.attrib.get('spacing', 0))
        for c in tag.getchildren():
            if c.tag == "image":
                # create a tileset from the image atlas
                path = resource.find_file(c.attrib['source'])
                tileset = TileSet.from_atlas(name, firstgid, path, tile_width,
                                             tile_height, row_padding=spacing,
                                             column_padding=spacing)
                # TODO consider adding the individual tiles to the resource?
                tilesets.append(tileset)
                resource.add_resource(name, tileset)
            elif c.tag == 'tile':
                # add properties to tiles in the tileset
                gid = tileset.firstgid + int(c.attrib['id'])
                tile = tileset[gid]
                props = c.find('properties')
                if props is None:
                    continue
                for p in props.findall('property'):
                    # store additional properties.
                    name = p.attrib['name']
                    value = p.attrib['value']
                    # TODO consider more type conversions?
                    if value.isdigit():
                        value = int(value)
                    tile.properties[name] = value

    # now load all the layers
    for layer in map.findall('layer'):
        data = layer.find('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        encoding = data.attrib.get('encoding')
        compression = data.attrib.get('compression')
        if encoding is None:
            # tiles data as xml
            data = [int(tile.attrib.get('gid')) for tile in data.findall('tile')]
        else:
            data = data.text.strip()
            if encoding == 'csv':
                data.replace('\n', '')
                data = [int(s) for s in data.split(',')]
            elif encoding == 'base64':
                data = decode_base64(data)
                if compression == 'zlib':
                    data = decompress_zlib(data)
                elif compression == 'gzip':
                    data = decompress_gzip(data)
                elif compression is None:
                    pass
                else:
                    raise ResourceError('Unknown compression method: %r' % compression)
                data = struct.unpack(str('<%di' % (len(data)//4)), data)
            else:
                raise TmxUnsupportedVariant("Unsupported tiles layer format " +
                                            "use 'csv', 'xml' or one of " +
                                            "the 'base64'")

        assert len(data) == width * height

        cells = [[None] * height for x in range(width)]
        for n, gid in enumerate(data):
            if gid < 1:
                tile = None
            else:
                # UGH
                for ts in tilesets:
                    if gid in ts:
                        tile = ts[gid]
                        break
            i = n % width
            j = height - (n//width + 1)
            cells[i][j] = cell_cls(i, j, tile_width, tile_height, {}, tile)

        id = layer.attrib['name']

        m = layer_cls(id, tile_width, tile_height, cells, None, {})
        m.visible = int(layer.attrib.get('visible', 1))

        resource.add_resource(id, m)

    # finally, object groups
    for tag in map.findall('objectgroup'):
        layer = TmxObjectLayer.fromxml(tag, tilesets, map_height_pixels)
        resource.add_resource(layer.name, layer)

    return resource

#
# XML PROPERTY PARSING
#


def text_to_4tuple_int(s):
    s = s.strip()
    s = s[1:-1]
    res = tuple([int(v) for v in s.split(',')])
    for e in res:
        assert 0 <= e <= 255
    return res


def color4_to_text(v):
    return repr(v)

_xml_to_python = dict(
    # built in types
    unicode=unicode,
    int=int,
    float=float,
    bool=lambda value: value != "False",
    # custom types
    color4=text_to_4tuple_int,
)
_python_to_xml = {
    # built in types
    str: unicode,
    unicode: unicode,
    int: repr,
    float: repr,
    bool: repr,
    # custom types
    'color4': color4_to_text,
}
_xml_type = {
    # type is the type of value
    str: 'unicode',
    unicode: 'unicode',
    int: 'int',
    float: 'float',
    bool: 'bool',
    # special cases, type from property name
    'color4': 'color4',
}


def _handle_properties(tag):
    """returns the properties dict reading from the etree node tag

    :Parameters:
        `tag` : xml.etree.ElementTree
            node from which the properties are obtained
    """
    properties = {}
    for node in tag.findall('./property'):
        name = node.get('name')
        type = node.get('type') or 'unicode'
        value = node.get('value')
        if name is None:
            raise TilesPropertyWithoutName("\nnode:\n%s" % ElementTree.tostring(node))
        if value is None:
            raise TilesPropertyWithoutValue("\nnode:\n%s" % ElementTree.tostring(node))
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
            raise ValueError('invalid child')

        if child.get('size'):
            width, height = map(int, child.get('size').split('x'))
        elif d_width is None:
            raise ValueError('atlas or subimage must specify size')
        else:
            width, height = d_width, d_height

        x, y = map(int, child.get('offset').split(','))
        image = atlas.get_region(x, y, width, height)

        # set texture clamping to avoid mis-rendering subpixel edges
        image.texture.id
        gl.glBindTexture(image.texture.target, image.texture.id)
        gl.glTexParameteri(image.texture.target,
                           gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(image.texture.target,
                           gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        # save the image off and set properties
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
    """Tiles hold an image and some optional properties.
    """
    def __init__(self, id, properties, image, offset=None):
        self.id = id
        self.properties = properties
        self.image = image
        self.offset = offset

    def __repr__(self):
        return '<%s object at 0x%x id=%r offset=%r properties=%r>' % (
            self.__class__.__name__, id(self), self.id, self.offset, self.properties)


class TileSet(dict):
    """Contains a set of Tile objects referenced by some id.
    """
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties

    tile_id = 0

    @classmethod
    def generate_id(cls):
        cls.tile_id += 1
        return str(cls.tile_id)

    def add(self, properties, image, id=None):
        """Add a new Tile to this TileSet, generating a unique id if
        necessary.

        Returns the Tile instance.
        """
        if id is None:
            id = self.generate_id()
        self[id] = Tile(id, properties, image)
        return self[id]

    @classmethod
    def from_atlas(cls, name, firstgid, file, tile_width, tile_height, row_padding=0, column_padding=0):
        image = pyglet.image.load(file)
        rows = (image.height + row_padding) // (tile_height + row_padding)
        columns = (image.width + column_padding) // (tile_width + column_padding)
        image_grid = pyglet.image.ImageGrid(image, rows, columns,
                                            row_padding=row_padding,
                                            column_padding=column_padding)
        atlas = pyglet.image.TextureGrid(image_grid)
        id = firstgid
        ts = cls(name, {})
        ts.firstgid = firstgid
        for j in range(rows - 1, -1, -1):
            for i in range(columns):
                tile_image = image.get_region(atlas[j, i].x,
                                              atlas[j, i].y,
                                              atlas[j, i].width,
                                              atlas[j, i].height)

                # Set texture clamping to avoid mis-rendering subpixel edges
                gl.glBindTexture(tile_image.texture.target, id)
                gl.glTexParameteri(tile_image.texture.target,
                                   gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameteri(tile_image.texture.target,
                                   gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

                ts[id] = Tile(id, {}, tile_image)
                id += 1
        return ts

#
# RECT AND HEX MAPS
#


@Resource.register_factory('rectmap')
# TODO: more diagnostics for malformed files; by example when a columm has less
# cells than expected
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
            if tile:
                tile = resource.get_resource(tile)
            else:
                tile = None
            properties = _handle_properties(cell)
            c.append(RectCell(i, j, width, height, properties, tile))

    properties = _handle_properties(tag)
    m = RectMapLayer(id, width, height, cells, origin, properties)
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
            if tile:
                tile = resource.get_resource(tile)
            else:
                tile = None
            properties = _handle_properties(cell)
            c.append(HexCell(i, j, None, height, properties, tile))

    properties = _handle_properties(tag)
    m = HexMapLayer(id, None, height, cells, origin, properties)
    resource.add_resource(id, m)

    return m


def hex_width(height):
    """Determine a regular hexagon's width given its height.
    """
    return int(height / sqrt(3) * 2)


class MapLayer(cocos.layer.ScrollableLayer):
    """Base class for Maps.

    Maps are comprised of tiles and can figure out which tiles are required to
    be rendered on screen.

    Both rect and hex maps have the following attributes::

        id              -- identifies the map in XML and Resources
        (width, height) -- size of map in cells
        (px_width, px_height)      -- size of map in pixels
        (tw, th)        -- size of each cell in pixels
        (origin_x, origin_y, origin_z)  -- offset of map top left from origin in pixels
        cells           -- array [i][j] of Cell instances
        debug           -- display debugging information on cells
        properties      -- arbitrary properties

    The debug flag turns on textual display of data about each visible cell
    including its cell index, origin pixel and any properties set on the cell.
    """
    def __init__(self, properties):
        self._sprites = {}
        self.properties = properties
        super(MapLayer, self).__init__()

    def __contains__(self, key):
        return key in self.properties

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def set_dirty(self):
        # re-calculate the sprites to draw for the view
        self._sprites.clear()
        self._update_sprite_set()

    def set_view(self, x, y, w, h, viewport_x=0, viewport_y=0):
        # invoked by ScrollingManager.set_focus()
        super(MapLayer, self).set_view(x, y, w, h, viewport_x, viewport_y)
        self._update_sprite_set()

    def get_visible_cells(self):
        """Given the current view in map-space pixels, transform it based
        on the current screen-space transform and figure the region of
        map-space pixels currently visible.

        Pass to get_in_region to return a list of Cell instances.
        """
        # XXX refactor me away
        x, y = self.view_x, self.view_y
        w, h = self.view_w, self.view_h
        return self.get_in_region(x, y, x + w, y + h)

    def is_visible(self, rect):
        """Determine whether the indicated rect (with .x, .y, .width and
        .height attributes) located in this Layer is visible.
        """
        x, y = rect.x, rect.y
        if x + rect.width < self.view_x:
            return False
        if y + rect.height < self.view_y:
            return False
        if x > self.view_x + self.view_w:
            return False
        if y > self.view_y + self.view_h:
            return False
        return True

    debug = False

    def set_debug(self, debug):
        self.debug = debug
        self._update_sprite_set()

    def set_cell_opacity(self, i, j, opacity):
        cell = self.get_cell(i, j)
        if cell is None:
            return
        if 'color4' in cell.properties:
            r, g, b, a = cell.properties['color4']
        else:
            r, g, b = (0, 0, 0)
        cell.properties['color4'] = (r, g, b, opacity)
        key = cell.origin[:2]
        if key in self._sprites:
            self._sprites[key].opacity = opacity

    def set_cell_color(self, i, j, color):
        cell = self.get_cell(i, j)
        if cell is None:
            return
        if 'color4' in cell.properties:
            a = cell.properties['color4'][3]
            r, g, b = color
        else:
            a = 255
            r, g, b = color
        cell.properties['color4'] = (r, g, b, a)
        key = cell.origin[:2]
        if key in self._sprites:
            self._sprites[key].color = color

    def _update_sprite_set(self):
        # update the sprites set
        keep = set()
        for cell in self.get_visible_cells():
            cx, cy = key = cell.origin[:2]
            keep.add(key)
            if cell.tile is None:
                continue
            if key in self._sprites:
                s = self._sprites[key]
            else:
                s = pyglet.sprite.Sprite(cell.tile.image,
                                         x=cx, y=cy, batch=self.batch)
                if 'color4' in cell.properties:
                    r, g, b, a = cell.properties['color4']
                    s.color = (r, g, b)
                    s.opacity = a
                self._sprites[key] = s

            if self.debug:
                if getattr(s, '_label', None):
                    continue
                label = [
                    'cell=%d,%d' % (cell.i, cell.j),
                    'origin=%d,%d px' % (cx, cy),
                ]
                for p in cell.properties:
                    label.append('%s=%r' % (p, cell.properties[p]))
                if cell.tile is not None:
                    for p in cell.tile.properties:
                        label.append('%s=%r' % (p, cell.tile.properties[p]))
                lx, ly = cell.topleft
                s._label = pyglet.text.Label(
                    '\n'.join(label), multiline=True, x=lx, y=ly,
                    bold=True, font_size=8, width=cell.width,
                    batch=self.batch)
            else:
                s._label = None
        for k in list(self._sprites):
            if k not in keep and k in self._sprites:
                self._sprites[k]._label = None
                del self._sprites[k]

    def find_cells(self, **requirements):
        """Find all cells that match the properties specified.

        For example:

           map.find_cells(player_start=True)

        Return a list of Cell instances.
        """
        r = []
        for col in self.cells:
            for cell in col:
                for k in requirements:
                    if cell.get(k) != requirements[k]:
                        break
                else:
                    r.append(cell)
        return r


class RegularTesselationMap(object):
    """A regularly tesselated map that allows access to its cells by index
    (i, j).
    """
    def get_cell(self, i, j):
        """ Return Cell at cell pos=(i, j).

        Return None if out of bounds."""
        if i < 0 or j < 0:
            return None
        try:
            return self.cells[i][j]
        except IndexError:
            return None


class RectMap(RegularTesselationMap):
    """Rectangular map.

    Cells are stored in column-major order with y increasing up,
    allowing [i][j] addressing::

     +---+---+---+
     | d | e | f |
     +---+---+---+
     | a | b | c |
     +---+---+---+

    Thus cells = [['a', 'd'], ['b', 'e'], ['c', 'f']]

    (and thus the cell at (0, 0) is 'a' and (0, 1) is 'd')
    """
    def __init__(self, id, tw, th, cells, origin=None, properties=None):
        """
        :Parameters:
            `id` : xml id
                node id
            `tw` : int
                number of colums in cells
            `th` : int
                number of rows in cells
            `cells` : container that supports cells[i][j]
                elements are stored in column-major order with y increasing up
            `origin` : (int, int, int)
                cell block offset x,y,z ; default is (0,0,0)
            `properties` : dict
                arbitrary properties
                if saving to XML, keys must be unicode or 8-bit ASCII strings
        """
        self.properties = properties or {}
        self.id = id
        self.tw, self.th = tw, th
        if origin is None:
            origin = (0, 0, 0)
        self.origin_x, self.origin_y, self.origin_z = origin
        self.cells = cells
        self.px_width = len(cells) * tw
        self.px_height = len(cells[0]) * th

    def get_in_region(self, left, bottom, right, top):
        """Return cells that intersects the rectangle left, bottom, right, top
        in an area greater than zero

        (left, bottom) and (right, top) are the lower left and upper right
        corners respectively, in map's coordinate space, unmodified by screen,
        layer or view transformations

        Return a list of Cell instances.

        When the rectangle has area zero results are a bit inconsistent:
            A rectangle which is a point intersects no cell
            A rectangle which is a segment and overlaps the cell boundaries
            intersects no cells
            A rectangle which is a segment and don't overlaps the cell
            boundaries intersects some cells: the ones that the open segment
            intersects
        """
        ox = self.origin_x
        oy = self.origin_y
        left = max(0, (left - ox) // self.tw)
        bottom = max(0, (bottom - oy) // self.th)
        right = min(len(self.cells), ceil(float(right - ox) / self.tw))
        top = min(len(self.cells[0]), ceil(float(top - oy) / self.th))
        return [self.cells[i][j]
                for i in range(int(left), int(right))
                for j in range(int(bottom), int(top))]

    def get_key_at_pixel(self, x, y):
        """returns the grid coordinates for the hex that covers the point (x, y)"""
        return (int((x - self.origin_x) // self.tw),
                int((y - self.origin_y) // self.th))

    def get_at_pixel(self, x, y):
        """ Return Cell at pixel px=(x,y) on the map.

        The pixel coordinate passed in is in the map's coordinate space,
        unmodified by screen, layer or view transformations.

        Return None if out of bounds.
        """
        return self.get_cell(*self.get_key_at_pixel(x, y))

    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def get_neighbor(self, cell, direction):
        """Get the neighbor Cell in the given direction (dx, dy) which
        is one of self.UP, self.DOWN, self.LEFT or self.RIGHT.

        Returns None if out of bounds.
        """
        dx, dy = direction
        return self.get_cell(cell.i + dx, cell.j + dy)

    def get_neighbors(self, cell, diagonals=False):
        """Get all cells touching the sides of the nominated cell.

        If "diagonals" is True then return the cells touching the corners
        of this cell too.

        Return a dict with the directions (self.UP, self.DOWN, etc) as keys
        and neighbor cells as values.
        """
        r = {}
        if diagonals:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        direction = (dx, dy)
                        r[direction] = self.get_cell(cell.i + dx, cell.j + dy)
        else:
            for direction in (self.UP, self.RIGHT, self.LEFT, self.DOWN):
                dx, dy = direction
                r[direction] = self.get_cell(cell.i + dx, cell.j + dy)
        return r

    # TODO: add checks to ensure good html. By example, what if cell is None?
    def _as_xml(self, root):
        """stores a XML representation of itself as child of root with type rectmap

        """
        m = ElementTree.SubElement(root, 'rectmap', id=self.id,
                                   tile_size='%dx%d' % (self.tw, self.th),
                                   origin='%s,%s,%s' % (self.origin_x, self.origin_y, self.origin_z))
        m.tail = '\n'

        # map properties
        for k in self.properties:
            v = self.properties[k]
            t = type(v)
            v = _python_to_xml[t](v)
            p = ElementTree.SubElement(m, 'property', name=k, value=v,
                                       type=_xml_type[t])
            p.tail = '\n'

        # columns / cells
        for column in self.cells:
            c = ElementTree.SubElement(m, 'column')
            c.tail = '\n'
            for cell in column:
                cell._as_xml(c)


class RectMapLayer(RectMap, MapLayer):
    """A renderable, scrollable rect map.
    """
    def __init__(self, id, tw, th, cells, origin=None, properties=None):
        RectMap.__init__(self, id, tw, th, cells, origin, properties)
        MapLayer.__init__(self, properties)


class RectMapCollider(object):
    """This class implements collisions between a moving rect object and a
    tilemap.
    """
    def collide_bottom(self, dy):
        pass

    def collide_left(self, dx):
        pass

    def collide_right(self, dx):
        pass

    def collide_top(self, dy):
        pass

    def collide_map(self, map, last, new, dx, dy):
        """Collide a rect with the given RectMap map.

        Apart from "map" the arguments are as per `do_collision`.

        Mutates the new rect to conform with the map.

        Returns the (possibly modified) (dx, dy)
        """
        tested = set()
        cells = map.get_in_region(*(new.bottomleft + new.topright))
        for cell in cells:
            if cell is None or cell.tile is None or not cell.intersects(new):
                continue
            tested.add(cell)
            dx, dy = self.do_collision(cell, last, new, dx, dy)
        cells_collide_later = [cell for cell in tested 
                            if hasattr(cell, 'collide_later')]
        for cell in cells_collide_later:
            if cell.intersects(new):
                dx, dy = self.do_collision(cell, last, new, dx, dy)
            del cell.collide_later
        return dx, dy

    def do_collision(self, cell, last, new, dx, dy):
        """Collide a Rect moving from "last" to "new" with the given map
        RectCell "cell". The "dx" and "dy" values may indicate the velocity
        of the moving rect.

        The RectCell must have the boolean properties "top", "left",
        "bottom" and "right" for those sides which the rect should collide.

        If there is no collision then nothing is done.

        If there is a collision:

        1. The "new" rect's position will be modified to its closest position
           to the side of the cell that the collision is on, and
        2. If the "new" rect position should be modified on both axis, then 
           nothing is done but the cell is flagged with an attribute 
           collide_later = True. This collision resolution should be treated 
           last, and collide_map is responsible to call again this function 
           on the flagged cell. This will force this function to move the 
           "new" rect on the axis requiring the smallest displacement.
           If the displacement is the same on both axis, move on both axis.
        3. If the "dx" and "dy" values are passed in the methods
           collide_<side> will be called to indicate that the rect has
           collided with the cell on the rect's side indicated. The value
           passed to the collide method will be a *modified* distance based
           on the position of the rect after collision (according to step
           #1).

        Mutates the new rect to conform with the map.

        Returns the (possibly modified) (dx, dy)
        """
        g = cell.get
        dx_correction = dy_correction = 0.0
        if g('top') and last.bottom >= cell.top and new.bottom < cell.top:
            dy_correction = cell.top - new.bottom
        elif g('bottom') and last.top <= cell.bottom and new.top > cell.bottom:
            dy_correction = cell.bottom - new.top
        if g('left') and last.right <= cell.left and new.right > cell.left:
            dx_correction = cell.left - new.right
        elif g('right') and last.left >= cell.right and new.left < cell.right:
            dx_correction = cell.right - new.left
        
        if dx_correction != 0.0 and dy_correction != 0.0:
            # Correction on both axis
            if hasattr(cell, 'collide_later'):
                if abs(dx_correction) < abs(dy_correction):
                    # do correction only on X (below)
                    dy_correction = 0.0
                elif abs(dy_correction) < abs(dx_correction):
                     # do correction only on Y (below)
                    dx_correction = 0.0
                else:
                    # let both corrections happen below
                    pass
            else:
                cell.collide_later = True
                return dx, dy

        if dx_correction != 0.0:
            # Correction on X axis
            new.left += dx_correction
            dx += dx_correction
            if dx_correction > 0.0:
                self.collide_left(dx)
            else:
                self.collide_right(dx)
        if dy_correction != 0.0:
            # Correction on Y axis
            new.top += dy_correction
            dy += dy_correction
            if dy_correction > 0.0:
                self.collide_bottom(dy)
            else:
                self.collide_top(dy)
        return dx, dy


class Cell(object):
    """Base class for cells from rect and hex maps.

    Common attributes::

        i, j            -- index of this cell in the map
        position        -- the above as a tuple
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Properties are available through the dictionary interface, ie. if the
    cell has a property 'cost' then you may access it as:

        cell['cost']

    You may also set properties in this way and use the .get() method to
    supply a default value.

    If the named property does not exist on the cell it will be looked up
    on the cell's tile.
    """
    def __init__(self, i, j, width, height, properties, tile):
        self.width, self.height = width, height
        self.i, self.j = i, j
        self.properties = properties
        self.tile = tile

    @property
    def position(self):
        return self.i, self.j

    def _as_xml(self, parent):
        c = ElementTree.SubElement(parent, 'cell')
        c.tail = '\n'
        if self.tile:
            c.set('tile', self.tile.id)
        for k in self.properties:
            v = self.properties[k]
            if k == 'color4':
                t = 'color4'
            else:
                t = type(v)
            v = _python_to_xml[t](v)
            ElementTree.SubElement(c, 'property', name=k, value=v,
                                   type=_xml_type[t])

    def __contains__(self, key):
        if key in self.properties:
            return True
        return key in self.tile.properties

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        elif self.tile is not None and key in self.tile.properties:
            return self.tile.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get(self, key, default=None):
        if key in self.properties:
            return self.properties[key]
        if self.tile is None:
            return default
        return self.tile.properties.get(key, default)

    def __repr__(self):
        return '<%s object at 0x%x (%g, %g) properties=%r tile=%r>' % (
            self.__class__.__name__, id(self), self.i, self.j, self.properties, self.tile)


class RectCell(Rect, Cell):
    """A rectangular cell from a MapLayer.

    Cell attributes::
    
        i, j            -- index of this cell in the map
        x, y            -- bottom-left pixel
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    The cell may have the standard properties "top", "left", "bottom" and
    "right" which are booleans indicating that those sides are impassable.
    These are used by RectCellCollider.

    Note that all pixel attributes are *not* adjusted for screen,
    view or layer transformations.
    """
    def __init__(self, i, j, width, height, properties, tile):
        Rect.__init__(self, i * width, j * height, width, height)
        Cell.__init__(self, i, j, width, height, properties, tile)

    # other properties are read-only
    origin = property(Rect.get_origin)
    top = property(Rect.get_top)
    bottom = property(Rect.get_bottom)
    center = property(Rect.get_center)
    midtop = property(Rect.get_midtop)
    midbottom = property(Rect.get_midbottom)
    left = property(Rect.get_left)
    right = property(Rect.get_right)
    topleft = property(Rect.get_topleft)
    topright = property(Rect.get_topright)
    bottomleft = property(Rect.get_bottomleft)
    bottomright = property(Rect.get_bottomright)
    midleft = property(Rect.get_midleft)
    midright = property(Rect.get_midright)


class HexMap(RegularTesselationMap):
    """MapLayer with flat-top, regular hexagonal cells.

    Calculated attributes::

      edge_length -- length of an edge in pixels = int(th / sqrt(3))
      tw          -- with of a "tile" in pixels = edge_length * 2

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map::

          /d\ /h\          .
        /b\_/f\_/          .
        \_/c\_/g\          .
        /a\_/e\_/          .
        \_/ \_/            .

    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]

    (and this the cell at (0, 0) is 'a' and (1, 1) is 'd')
    """
    def __init__(self, id, th, cells, origin=None, properties=None):
        properties = properties or {}
        self.id = id
        self.th = th
        if origin is None:
            origin = (0, 0, 0)
        self.origin_x, self.origin_y, self.origin_z = origin
        self.cells = cells

        # figure some convenience values
        s = self.edge_length = int(th / sqrt(3))
        self.tw = self.edge_length * 2

        # now figure map dimensions
        width = len(cells)
        height = len(cells[0])
        self.px_width = self.tw + (width - 1) * (s + s//2)
        self.px_height = height * self.th
        if not width % 2:
            self.px_height += (th // 2)

    def get_in_region(self, left, bottom, right, top):
        """Return cells (in [column][row]) that are within the pixel bounds
        specified by the bottom-left (left, bottom) and top-right (right, top) corners.
        """
        ox = self.origin_x
        oy = self.origin_y
        col_width = self.tw//2 + self.tw//4
        left = max(0, (left - ox)//col_width - self.tw//4)
        bottom = max(0, (bottom - oy)//self.th - 1)
        right = min(len(self.cells), right//col_width + 1)
        top = min(len(self.cells[0]), top//self.th + 1)
        return [self.cells[i][j] for i in range(left, right) for j in range(bottom, top)]

    # XXX add get_from_screen

    def get_key_at_pixel(self, x, y):
        """returns the grid coordinates for the hex that covers the point (x, y)

        Reference:
            Hexagonal grid math, by Ruslan Shestopalyuk
            http://blog.ruslans.com/2011/02/hexagonal-grid-math.html
        """
        radius = self.edge_length
        side = (self.tw * 3) // 4
        height = self.th

        ci = int(floor(x / side))
        cx = int(x - side*ci)

        ty = int(y - (ci % 2) * height / 2.0)
        cj = int(floor(1.0 * ty / height))
        cy = ty - height * cj

        if cx <= abs(radius/2.0 - radius*cy/height):
            cj = cj + (ci % 2) - (1 if (cy < height / 2.0) else 0)
            ci = ci - 1
        return ci, cj

    def get_at_pixel(self, x, y):
        """Get the Cell at pixel (x,y).

        Return None if out of bounds."""
        return self.get_cell(*self.get_key_at_pixel(x, y))

    UP = 'up'
    DOWN = 'down'
    UP_LEFT = 'up left'
    UP_RIGHT = 'up right'
    DOWN_LEFT = 'down left'
    DOWN_RIGHT = 'down right'

    def get_neighbor(self, cell, direction):
        """Get the neighbor HexCell in the given direction which
        is one of self.UP, self.DOWN, self.UP_LEFT, self.UP_RIGHT,
        self.DOWN_LEFT or self.DOWN_RIGHT.

        Return None if out of bounds.
        """
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
            raise ValueError('Unknown direction %r' % direction)

    def get_neighbors(self, cell):
        """Get all neighbor cells for the nominated cell.

        Return a dict with the directions (self.UP, self.DOWN, etc) as keys
        and neighbor cells as values.
        """
        r = {}
        for direction in (self.UP_LEFT, self.UP, self.UP_RIGHT,
                          self.DOWN_LEFT, self.DOWN, self.DOWN_RIGHT):
            dx, dy = direction
            r[direction] = self.get_cell(cell.i + dx, cell.j + dy)
        return r


class HexMapLayer(HexMap, MapLayer):
    """A renderable, scrollable tile map covered by hexagonal tiles

    While visually the tiles look hexagonal, the texture that draws each
    tile is rectangular and should comply:

      + depicts an hexagon with upper and lower sides paralel to the x-axis
      + area out of the hexagon should be transparent
      + tile size must comply width == int(height / sqrt(3) * 2)

    Be warned that some hexagonal tilesets found in the net use other
    proportions or the pointy orientation ( left and right sides paralel to
    the y-axis) ; neither will work with HexMapLayer

    The Layer has a calculated attribute::

     edge_length -- length of an edge in pixels = int(th / sqrt(3))
     tw          -- with of a "tile" in pixels = edge_length * 2

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map::

              /d\ /h\        .
            /b\_/f\_/        .
            \_/c\_/g\        .
            /a\_/e\_/        .
            \_/ \_/          .

    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
    """
    # param 'ignored' only to match signature of RectmapLayer; not used
    def __init__(self, id, ignored, th, cells, origin=None, properties=None):
        HexMap.__init__(self, id, th, cells, origin, properties)
        MapLayer.__init__(self, properties)


# Note that we always add below (not subtract) so that we can try to
# avoid accumulation errors due to rounding ints. We do this so
# we can each point at the same position as a neighbor's corresponding
# point.
class HexCell(Cell):
    """A flat-top, regular hexagon cell from a HexMap.

    Cell attributes::
    
        i, j            -- index of this cell in the map
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Read-only attributes::
    
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
    """
    # param 'ignored' only to match signature of RectCell; not used
    def __init__(self, i, j, ignored, height, properties, tile):
        width = hex_width(height)
        Cell.__init__(self, i, j, width, height, properties, tile)

    def get_origin(self):
        x = self.i * (self.width//2 + self.width//4)
        y = self.j * self.height
        if self.i % 2:
            y += self.height // 2
        return x, y
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
        return x + self.width//2, y + self.height//2
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        x, y = self.get_origin()
        return x + self.width//2, y + self.height
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        x, y = self.get_origin()
        return x + self.width//2, y
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        x, y = self.get_origin()
        return x, y + self.height//2
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        x, y = self.get_origin()
        return x + self.width, y + self.height//2
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        x, y = self.get_origin()
        return x + self.width//4, y + self.height
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        x, y = self.get_origin()
        return x + self.width//2 + self.width//4, y + self.height
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        x, y = self.get_origin()
        return x + self.width//4, y
    bottomleft = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        x, y = self.get_origin()
        return x + self.width//2 + self.width//4, y
    bottomright = property(get_bottomright)

    # ro, middle of side in pixels, (x, y)
    def get_midtopleft(self):
        x, y = self.get_origin()
        return x + self.width//8, y + self.height//2 + self.height//4
    midtopleft = property(get_midtopleft)

    # ro, middle of side in pixels, (x, y)
    def get_midtopright(self):
        x, y = self.get_origin()
        return (x + self.width//2 + self.width//4 + self.width//8,
                y + self.height//2 + self.height//4)
    midtopright = property(get_midtopright)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomleft(self):
        x, y = self.get_origin()
        return x + self.width//8, y + self.height//4
    midbottomleft = property(get_midbottomleft)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomright(self):
        x, y = self.get_origin()
        return (x + self.width//2 + self.width//4 + self.width//8,
                y + self.height//4)
    midbottomright = property(get_midbottomright)


def parse_tmx_points(tag, obj_x, obj_y):
    """parses tmx tag points into left, bottom, right, top, points

    :Parameters:
        `tag` : xml tag
            assumed an object tag
        `obj_x` :
            object x position in gl coordinates
        `obj_y` :
            object y position in gl coordinates

    :Returns: tuple (left, bottom, width, height, points)
        left: leftmost x-position in points, gl coordinates system
        bottom: bottommost y-position in points, gl coordinates system
        width: width of point's enclosing box
        height: height of point's enclosing box
        points: list of points in a gl coordinates system relative to (left, bottom)
    """
    points_string = tag.attrib['points']
    points_parts = points_string.split(' ')
    # points, absolute position
    pa = []
    for pair in points_parts:
        coords = pair.split(',')
        pa.append((float(coords[0]) + obj_x, -float(coords[1]) + obj_y))

    left = min([x for x, y in pa])
    bottom = min([y for x, y in pa])
    right = max([x for x, y in pa])
    top = max([y for x, y in pa])
    width = right - left + 1
    height = top - bottom + 1

    # points, relative to (bottom, left)
    points = [(x - left, y - bottom) for x, y in pa]
    return left, bottom, width, height, points


def tmx_coords_to_gl(x, y, map_height):
    return x, map_height - y


class TmxObject(Rect):
    """Represents an object in a TMX object layer.

    Instances of this class are ussually constructed by calling
    TmxObject.fromxml

    Theres no validation of data pased to __init__::

        tmxtype: one of 'ellipse', 'polygon', 'polyline', 'rect', 'tile'
        name: An arbitrary string. The object's 'name' field in Tiled Editor.
        usertype: An arbitrary string. The object's 'type' field in Tiled Editor.
        x: The x coordinate of the bottomleft object's Axis Aligned Bounding Box.
        y: The y coordinate of the bottomleft object's Axis Aligned Bounding Box.
        width: The width of the object in pixels (defaults to 0).
        height: The height of the object in pixels (defaults to 0).
        gid: An reference to a tile (optional).
        visible: Whether the object is shown (1) or hidden (0). Defaults to 1.
        points: a sequence of coords (x, y) relative to bottomleft  thas enumerates
        the vertices in a 'polygon' or 'polyline'.

    A 'rect' AABB is itself, so x,y is it's bottomleft corner.
    """
    def __init__(self, tmxtype, usertype, x, y, width=0, height=0, name=None,
                 gid=None, tile=None, visible=1, points=None):
        if tile:
            width = tile.image.width
            height = tile.image.height
        super(TmxObject, self).__init__(x, y, width, height)
        self.tmxtype = tmxtype
        self.px = x
        self.py = y
        self.usertype = usertype
        self.name = name
        self.gid = gid
        self.tile = tile
        self.visible = visible
        self.points = points
        self.properties = {}

        self._added_properties = {}
        self._deleted_properties = set()

    def __repr__(self):
        if self.tile:
            return '<TmxObject %s,%s %s,%s tile=%d>' % (self.px, self.py, self.width, self.height, self.gid)
        else:
            return '<TmxObject %s,%s %s,%s>' % (self.px, self.py, self.width, self.height)

    def __contains__(self, key):
        if key in self._deleted_properties:
            return False
        if key in self._added_properties:
            return True
        if key in self.properties:
            return True
        return self.tile and key in self.tile.properties

    def __getitem__(self, key):
        if key in self._deleted_properties:
            raise KeyError(key)
        if key in self._added_properties:
            return self._added_properties[key]
        if key in self.properties:
            return self.properties[key]
        if self.tile and key in self.tile.properties:
            return self.tile.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._added_properties[key] = value

    def __delitem__(self, key):
        self._deleted_properties.add(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    @classmethod
    def fromxml(cls, tag, tilesets, map_height):
        """
        :Parameters:
            `tag` : xml tag
                assumed an object tag
            `tileset` : enumerable giving tilesets
                only the tilesets used used by an object tile are needed, can be []
            `map_height` : int
                map height in pixels, needed to change coords from tmx to gl

        :Returns: a TmxObject instance
            attributes in the instance will store the info parsed from the class
        """
        # tiled uses origin at topleft map corner, convert to gl bottomleft origin
        left = float(tag.attrib['x'])
        top = map_height - float(tag.attrib['y'])
        bottom = None
        points = None

        if 'gid' in tag.attrib:
            tmxtype = 'tile'
            gid = int(tag.attrib['gid'])
            # UGH
            for ts in tilesets:
                if gid in ts:
                    tile = ts[gid]
                    break
            w = tile.image.width
            h = tile.image.height
        else:
            gid = None
            tile = None
            w = float(tag.attrib.get('width', 0))
            h = float(tag.attrib.get('height', 0))

            subtags = {}
            for c in tag.getchildren():
                subtags[c.tag] = c
            if 'ellipse' in subtags:
                tmxtype = 'ellipse'
            elif 'polygon' in subtags:
                tmxtype = 'polygon'
                left, bottom, w, h, points = parse_tmx_points(subtags['polygon'], left, top)
            elif 'polyline' in subtags:
                tmxtype = 'polyline'
                left, bottom, w, h, points = parse_tmx_points(subtags['polyline'], left, top)
            else:
                tmxtype = 'rect'

        if bottom is None:
            if tmxtype == 'tile':
                # special case, see https://github.com/bjorn/tiled/issues/91
                bottom = top
            else:
                bottom = top - h

        o = cls(tmxtype, tag.attrib.get('type'), left, bottom, w, h,
                tag.attrib.get('name'), gid, tile, int(tag.attrib.get('visible', 1)),
                points)

        props = tag.find('properties')
        if props is None:
            return o

        for c in props.findall('property'):
            # store additional properties.
            name = c.attrib['name']
            value = c.attrib['value']

            # TODO hax
            if value.isdigit():
                value = int(value)
            o.properties[name] = value
        return o

    def intersects(self, x1, y1, x2, y2):
        if x2 < self.px:
            return False
        if y2 < self.py:
            return False
        if x1 > self.px + self.width:
            return False
        if y1 > self.py + self.height:
            return False
        return True


class TmxObjectLayer(MapLayer):
    """A layer composed of basic primitive shapes.

    Actually encompasses a TMX <objectgroup> but even the TMX documentation
    refers to them as object layers, so I will.

    TmxObjectLayers have some basic properties::

        position - ignored (cannot be edited in the current Tiled editor)
        name - the name of the object group.
        color - the color used to display the objects in this group.
        opacity - the opacity of the layer as a value from 0 to 1.
        visible - whether the layer is shown (1) or hidden (0).
        objects - the objects in this Layer (TmxObject instances)
    """
    def __init__(self, name, color, objects, opacity=1,
                 visible=1, position=(0, 0)):
        MapLayer.__init__(self, {})
        self.name = name
        self.color = color
        self.objects = objects
        self.opacity = opacity
        self.visible = visible
        self.position = position

    def __repr__(self):
        return '<TmxObjectLayer "%s" at 0x%x>' % (self.name, id(self))

    @classmethod
    def fromxml(cls, tag, tilesets, map_height):
        color = tag.attrib.get('color')
        if color:
            color = p_html._parse_color(color)
        layer = cls(tag.attrib['name'], color, [],
                    float(tag.attrib.get('opacity', 1)),
                    int(tag.attrib.get('visible', 1)))
        for obj in tag.findall('object'):
            layer.objects.append(TmxObject.fromxml(obj, tilesets, map_height))
        for c in tag.findall('property'):
            # store additional properties.
            name = c.attrib['name']
            value = c.attrib['value']

            # TODO hax
            if value.isdigit():
                value = int(value)
            layer.properties[name] = value
        return layer

    def update(self, dt, *args):
        pass

    def find_cells(self, **requirements):
        """Find all objects with the given properties set.

        Called "find_cells" for compatibility with existing cocos tile API.
        """
        r = []
        for propname in requirements:
            for obj in self.objects:
                if obj and propname in obj or propname in self.properties:
                    r.append(obj)
        return r

    def match(self, **properties):
        """Find all objects with the given properties set to the given values.
        """
        r = []
        for propname in properties:
            for obj in self.objects:
                if propname in obj:
                    val = obj[propname]
                elif propname in self.properties:
                    val = self.properties[propname]
                else:
                    continue
                if properties[propname] == val:
                    r.append(obj)
        return r

    def collide(self, rect, propname):
        """Find all objects the rect is touching that have the indicated
        property name set.
        """
        r = []
        for obj in self.get_in_region(rect.left, rect.bottom, rect.right,
                                      rect.top):
            if propname in obj or propname in self.properties:
                r.append(obj)
        return r

    def get_in_region(self, left, bottom, right, top):
        """Return objects that are within the map-space
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        Return a list of TmxObject instances.
        """
        return [obj for obj in self.objects if obj.intersects(left, bottom, right, top)]

    def get_at(self, x, y):
        """Return the first object found at the nominated (x, y) coordinate.

        Return an TmxObject instance or None.
        """
        for obj in self.objects:
            if obj.contains(x, y):
                return obj

    def _update_sprite_set(self):
        self._sprites = {}
        color = self.color
        if color is None:
            color = [255] * 3
        color = tuple(color[:3] + [128])
        color_image = pyglet.image.SolidColorImagePattern(color)
        for cell in self.get_visible_cells():
            cx, cy = key = cell.origin[:2]
            if cell.tile:
                image = cell.tile.image
            else:
                image = color_image.create_image(int(cell.width), int(cell.height))

            if key not in self._sprites:
                self._sprites[key] = pyglet.sprite.Sprite(image, x=int(cx), y=int(cy),
                                                          batch=self.batch)


class TmxObjectMapCollider(RectMapCollider):
    def collide_map(self, map, last, new, dx, dy):
        """Collide a rect with the given TmxObjectLayer map.

        Apart from "map" the arguments are as per `do_collision`.

        Mutates the new rect to conform with the map.

        Returns the (possibly modified) (dx, dy)
        """
        self.resting = False
        tested = set()
        for cell in map.get_in_region(*(new.bottomleft + new.topright)):
            if cell is None or cell.tile is None:
                continue
            # don't re-test
            if cell in tested:
                continue
            tested.add(cell)
            dx, dy = self.do_collision(cell, last, new, dx, dy)
        return dx, dy
