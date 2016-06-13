from __future__ import division, print_function, unicode_literals

# important: set cocos_utest=1 in the environment before run.
# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']
import xml.etree.ElementTree as ET

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1 

import cocos
from cocos.director import director
import cocos.layer
from cocos.tiles import TmxObjectLayer, RectMapLayer

import pytest

director.init()

def is_equal_xml(a, b):
    "Compare if 2 XML ElementTree are identical"
    if a.tag != b.tag:
        return False
    if a.attrib != b.attrib:
        return False
    if a.text.strip() if a.text else "" != b.text.strip() if b.text else "":
        return False
    for ac, bc in zip(a, b):
        if not is_equal_xml(ac, bc):
            return False
    return True

class DummyTile(object):
    def __init__(self, _id):
        self.id = _id

@pytest.fixture(scope='session')
def tileset_filename(tmpdir_factory):
    "Make a temp xml file with a TileSet definition for testing."
    data = """\
<?xml version="1.0"?>
<resource>
    <tileset>
        <tile id="1" />
    </tileset>
</resource>
"""
    fn = tmpdir_factory.mktemp('data').join('tileset.xml')
    fn.write(data)
    return str(fn)

@pytest.fixture(scope='session')
def rectmap_filename(tmpdir_factory):
    "Make a temp xml file with a RectMap definition for testing."
    data = """\
<?xml version="1.0"?>
<resource>
    <tileset>
        <tile id="1" />
    </tileset>
    <rectmap id="walls" origin="0,0,1" tile_size="128x128">
        <column>
            <cell />
        </column>
    </rectmap>
</resource>
"""
    fn = tmpdir_factory.mktemp('data').join('rectmap.xml')
    fn.write(data)
    return str(fn)

@pytest.fixture
def tmxmap_filename(tmpdir_factory):
    data = """\
<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0" orientation="orthogonal" renderorder="right-down" width="9"
 height="6" tilewidth="128" tileheight="128" nextobjectid="19">
    <objectgroup name="test_object_layer">
    <object id="15" name="rect_1" x="353.717" y="197.333" width="64.05" 
      height="128"/>
 </objectgroup>
</map>
"""
    fn = tmpdir_factory.mktemp('data').join('objectmap.tmx')
    fn.write(data)
    return str(fn)




def test_resource_xml_save_header(rectmap_filename):
    resource = cocos.tiles.load(rectmap_filename)
    name, ext = rectmap_filename.split(".")
    saved_filename = name + "_saved." + ext
    resource.save_xml(saved_filename)

    with open(saved_filename) as f:
        text = f.read()
    assert text.startswith("<?xml version='1.0' encoding='utf-8'?>")

def test_resource_tmx_load_rectmap(tmxmap_filename):
    resource = cocos.tiles.load(tmxmap_filename)
    assert "test_object_layer" in resource
    assert isinstance(resource["test_object_layer"], TmxObjectLayer)
    assert "not_an_id" not in resource

def test_resource_xml_load_rectmap(rectmap_filename):
    resource = cocos.tiles.load(rectmap_filename)
    assert "walls" in resource
    assert isinstance(resource["walls"], RectMapLayer)
    assert "not_an_id" not in resource

def test_resource_xml_save_rectmap(rectmap_filename):
    resource = cocos.tiles.load(rectmap_filename)
    name, ext = rectmap_filename.split(".")
    saved_filename = name + "_saved." + ext
    resource.save_xml(saved_filename)

    saved_tree = ET.parse(saved_filename).getroot()
    original = ET.parse(rectmap_filename).getroot()
    assert is_equal_xml(saved_tree, original) is True

def test_resource_save_tileset(tileset_filename):
    resource = cocos.tiles.load(tileset_filename)
    name, ext = tileset_filename.split(".")
    saved_filename = name + "_saved." + ext
    resource.save_xml(saved_filename)

    saved_tree = ET.parse(saved_filename).getroot()
    original = ET.parse(tileset_filename).getroot()
    assert is_equal_xml(saved_tree, original) is True

def test_resource_xml_save_modified_rectmap(rectmap_filename):
    resource = cocos.tiles.load(rectmap_filename)

    rectmap = resource['walls']
    cell = rectmap.get_cell(0, 0)
    cell.tile = DummyTile('2')

    name, ext = rectmap_filename.split(".")
    saved_filename = name + "_saved_mod." + ext
    resource.save_xml(saved_filename)

    saved_tree = ET.parse(saved_filename).getroot()
    cell = saved_tree.find('rectmap//cell')
    assert cell.get('tile') == '2'
