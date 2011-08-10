import operator
import pprint

import cocos
import cocos.euclid as eu
import cocos.collision_model as cm

class BaseActor(cocos.sprite.Sprite):
    # loadable subclasses should set
    # ingame_type_id = '...'

    @classmethod
    def new_from_dict(cls, game, args, description_dict):
        """
        don't modify, autority is editor

        args provides aditional positional arguments that must reach the
        __init__. These arguments don't come from the stored map, they are
        generated at game runtime just before calling here.
        Look at the manual for extra info

        description_dict carries the info for this instantiation comming
        from the stored level  
        """
        desc = description_dict
        ingame_type_id = description_dict.pop('ingame_type_id')
        editor_type_id = description_dict.pop('editor_type_id')
        combo_type = (editor_type_id, ingame_type_id)
        editor_img = game['roles']['actor'][combo_type]['editor_img']
        # it is a pyglet resource, so use '/' always to concatenate
        ingame_img = 'data/images/' + editor_img
        cx = description_dict.pop('cx')
        cy = description_dict.pop('cy')
        all_args = [ingame_img, cx, cy]
        all_args.extend(args) 
        actor = cls(*all_args, **description_dict)
        return actor

    def __init__(self, default_img, cx, cy,
                 # custom, all-subclasses, provided at run-time arguments
                 level,
                 # editor mandated, dont touch 
                 visible_width=32, others={}):
        """
        Adding or removing parameters must follow special rules to not break
        load-store, look in the manual in secctions named 'Changing code'
        """
        # cx, cy, visible_width in world units
        super(BaseActor, self).__init__(default_img)
        center = eu.Vector2(cx, cy)
        self.cshape = cm.AARectShape(center, 1.0, 1.0)
        self.update_visible_width(visible_width)
        self.update_center(center)
        self.level = level
        # process 'others' if necesary
        #...

    def update_center(self, new_center):
        assert isinstance(new_center, eu.Vector2) 
        self.position = new_center
        self.cshape.center = new_center

    def update_visible_width(self, visible_width):
        self.visible_width = visible_width
        self.scale =  float(visible_width) / self.image.width
        rx = visible_width / 2.0
        ry = self.image.height / 2.0 * self.scale
        self.cshape.rx = rx
        self.cshape.ry = ry


class Player(BaseActor):
    ingame_type_id = 'player 00.01'

class EnemyWanderer(BaseActor):
    ingame_type_id = 'wanderer 00.01'

class EnemyChained(BaseActor):
    ingame_type_id = 'chained mons 00.01'

class Tree(BaseActor):
    ingame_type_id = 'tree 00.01'
    # old lime, best green
    eu_colors = [eu.Vector3(149,171,63), eu.Vector3(9,216,6)]

    def set_color_lerp_fraction(self, r):
        eu_color3 = r*Tree.eu_colors[0] + (1.0 - r)*Tree.eu_colors[1]
        color3 = [int(c) for c in eu_color3]
        self.color = color3

class Jewel(BaseActor):
    ingame_type_id = 'jewel 00.01'
    
