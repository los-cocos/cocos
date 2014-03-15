'''Cocos tileset generator

Usage: gentileset.py  <image_name> <tile_width> <tile_height> [<output.xml>]

This script generates a tileset xml file from a givend image, tile width and
height. If an output parameter is provided the generated xml is printed to
this file, if it's not the output is written to the standard output.

More info on the schema of the generated xml can be found on cocos.tiles
documentation.

'''

from __future__ import division, print_function, unicode_literals

from xml.dom.minidom import getDOMImplementation

def build_tileset_xml(image_name, image, tw, th):
    h_tiles = image.width // tw
    v_tiles = image.height // th
    
    dom = getDOMImplementation()

    doc = dom.createDocument(None, "resource", None)
    top_element = doc.documentElement
    
    atlas_element = doc.createElement('imageatlas')
    atlas_element.setAttribute('size', '%dx%d' % (tw, th))
    atlas_element.setAttribute('file', image_name)
    
    tileset_element = doc.createElement('tileset')
    
    for y in range(v_tiles):
        for x in range(h_tiles):
            id = "t%d" % (y*h_tiles + x)
            
            image_elm = doc.createElement('image')
            image_elm.setAttribute('id', 'i-%s' % id)
            image_elm.setAttribute('offset', '%d,%d' % (x*th, y*tw))
            atlas_element.appendChild(image_elm)
            
            tile_elm = doc.createElement('tile')
            tile_elm.setAttribute('id', str(id))
            
            image_ref_elm = doc.createElement('image')
            image_ref_elm.setAttribute('ref', 'i-%s' % id)
            
            tile_elm.appendChild(image_ref_elm)
            tileset_element.appendChild(tile_elm)
    
    top_element.appendChild(atlas_element)
    top_element.appendChild(tileset_element)
    
    return doc
    

if __name__ == "__main__":
    import sys
    import pyglet
    
    def exit(msg=None):
        if msg: print(msg)
        print("Usage: %s <image_name> <tile_width> <tile_height> [<output.xml>]" % sys.argv[0])
        sys.exit(1)
    
    if len(sys.argv) < 4:
        exit()
    
    image_name = sys.argv[1]
    try:
        tile_w, tile_h = int(sys.argv[2]), int(sys.argv[3])
    except ValueError:
        exit("<tile_width> and <tile_height> should be integers.")
    
    try:
        image = pyglet.image.load(image_name)
    except IOError:
        exit("Invalid image file '%s'" % image_name)
        
    if len(sys.argv) < 5:
        fname = 'output.xml'
    else:
        fname = sys.argv[4]

    try:
        output = open(fname, 'w')
    except IndexError:
        output = None
        
    doc = build_tileset_xml(image_name, image, tile_w, tile_h)
    print(doc.toprettyxml(), file=output)
    output.close()
    
