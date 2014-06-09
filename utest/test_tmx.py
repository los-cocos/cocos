# -*- coding: utf-8 -*-
""" Tests features of Tiled .tmx map files in cocos.tiles
Run the tests with pytest.
"""
from __future__ import division, print_function, unicode_literals

# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1

# will use the cocos in the same checkout, except if you move this file.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import xml.etree.ElementTree as ET
import cocos.layer
from cocos.tiles import TmxObject
from cocos.euclid import Vector2 as v2

class Test_TmxObject(object):
    # all object samples used a 4 x 3 grid, with tile size 64 x 32
    # so map_width = 64 * 4 = 256 and map_height = 32 * 4 = 128

    ## check 'usertype' is correct

    def test_fromxml__usertype__implicit(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.usertype == None

    def test_fromxml__usertype__explicit(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object type="custom type" x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.usertype == "custom type"

    def test_fromxml__usertype__explicit__encoding(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object type="\xc3\xad i with acute acent" x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.usertype == "í i with acute acent"

    ## check 'name' is correct

    def test_fromxml__name__implicit(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.name == None

    def test_fromxml__name__explicit(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object name="custom name" x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.name == "custom name"

    ## check 'tmxtype' is correct

    def test_fromxml__ellipse_tmxtype(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="128" y="34">
           <ellipse/>
          </object>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.tmxtype == "ellipse"

    def test_fromxml__polygon_tmxtype(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="98" y="46">
           <polygon points="0,0 24,-3 17,12"/>
          </object>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.tmxtype == "polygon"

    def test_fromxml__polyline_tmxtype(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="76" y="18">
           <polyline points="0,0 12,34 55,31"/>
          </object>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.tmxtype == "polyline"

    def test_fromxml__rect_tmxtype(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.tmxtype == "rect"

    def test_fromxml__tile_tmxtype(self):
        map_height = 128
        class TI(object):
            class IM(object):
                width = 64
                height = 32
            image = IM()
        tilesets = [{1: TI()}]
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object gid="1" x="154" y="43"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.tmxtype == "tile"

    ## check 'width' and 'height' are correct for the tmxtypes {'rect', 'ellipse'}
    ## Tested only 'rect', 'ellipse' uses the same codepath for 'width' and 'height'

    def test_fromxml__rect_width_and_height__00(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 0
        assert tmx_obj.height == 0

    def test_fromxml__rect_width_and_height__X0(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object name="bottom_left" x="0" y="96" width="12"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 12
        assert tmx_obj.height == 0

    def test_fromxml__rect_width_and_height__0Y(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object name="bottom_left" x="0" y="96" height="57"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 0
        assert tmx_obj.height == 57

    def test_fromxml__rect_width_and_height__XY(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object name="bottom_left" x="0" y="96" width="12" height="57"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 12
        assert tmx_obj.height == 57

    ## check 'width' and 'height' are correct for the tmxtypes
    ## {'polygon', 'polyline'}; Tested only 'polygon', 'polyline' uses the
    ## same codepath for 'width' and 'height'

    def test_fromxml__polygon_width_and_height(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="98" y="46">
           <polygon points="0,0 24,-3 17,12"/>
          </object>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 25
        assert tmx_obj.height == 16

    ## check 'width' and 'height' are correct for tmxtype 'tile'

    def test_fromxml__tile_width_and_height(self):
        map_height = 128
        class TI(object):
            class IM(object):
                width = 64
                height = 32
            image = IM()
        tilesets = [{1: TI()}]
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
            <object gid="1" x="154" y="43"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.width == 64
        assert tmx_obj.height == 32

    ## check 'px' is correct for 'rect', 'ellipse', 'tile'
    def test_fromxml__rect_px(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="256" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.px == 256

    ## check 'px' is correct for 'polygon', 'polyline'
    def test_fromxml__polygon_px(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="98" y="46">
           <polygon points="0,0 24,-3 17,12"/>
          </object>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.px == min([x+98 for x,y in tmx_obj.points])

    ## check 'py' is correct for 'rect', 'ellipse', 'tile'

    def test_fromxml__rect_py__height_0(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="64" y="0"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.py == map_height

        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="64" y="128"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.py == 0

    def test_fromxml__rect_py__height_nonzero(self):
        map_height = 128
        tilesets = None
        # topleft pixel in the map, covers [0.0, 1.0] x [0.0, 1.0] in Tiled space,
        # in gl coords covers [0.0, 1.0] x [mh-1, mh]  (mh=map_height)
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="0" y="0" width="1" height="1"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.py == map_height - 1

        # bottomleft pixel in the map, covers [0.0, 1.0] x [mh-1, mh] in Tiled space,
        # in gl coords covers [0.0, 1.0] x [0.0, 1.0]
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="0" y="127" width="1" height="1"/>
        """
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        assert tmx_obj.py == 0

    ## check 'py' is correct and 'points' are correct for 'polygon', 'polyline'
    def test_fromxml__polygon_px(self):
        map_height = 128
        tilesets = None
        obj_string = b"""<?xml version="1.0" encoding="UTF-8"?>
          <object x="98" y="46">
           <polygon points="0,0 -64,0 -64,32 0,32"/>
          </object>
        """
        vertices_tiled_relative = [v2(0,0), v2(-64,0), v2(-64,32), v2(0,32)]
        vertices_tiled_absolute = [v+v2(98, 46) for v in vertices_tiled_relative]
        vertices_gl_abs = [v2(x, map_height-y) for x,y in vertices_tiled_absolute]
        xml_obj = ET.fromstring(obj_string)
        tmx_obj = TmxObject.fromxml(xml_obj, tilesets, map_height)
        # on the other way,
        vertices_gl_relative = [v2(*p) for p in tmx_obj.points]
        pos = v2(tmx_obj.px, tmx_obj.py)
        vertices_gl_absolute = [ v+pos for v in vertices_gl_relative]
        # so it must hold
        assert vertices_gl_absolute == vertices_gl_abs
        # and, being (px, py) the bottomleft corner of bounding box must be
        assert 0 == min([y for x,y in tmx_obj.points])
