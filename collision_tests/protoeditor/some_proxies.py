import operator
import pprint

import cocos
import cocos.euclid as eu
import cocos.collision_model as cm

class ActorProxy(cocos.sprite.Sprite):
    editor_type_id = 'actorproxy 00.01'

    @classmethod
    def new_from_dict(cls, game, description_dict):
        desc = description_dict
        ingame_type_id = desc.pop('ingame_type_id')
        key = (cls.editor_type_id, ingame_type_id)
        editor_img = game['roles']['actor'][key]['editor_img']
        cx = desc.pop('cx')
        cy = desc.pop('cy')
        visible_width = desc.pop('visible_width')
        actor = ActorProxy(ingame_type_id, cx, cy, visible_width,
                           editor_img, **desc)
        return actor

    def __init__(self, ingame_type_id, cx, cy, visible_width,
                 ed_image, **others):
        # cx, cy, visible_width in world units
        super(ActorProxy, self).__init__(ed_image)
        self.ingame_type_id = ingame_type_id
        self.others = others
        center = eu.Vector2(cx, cy)
        self.cshape = cm.AARectShape(center, 1.0, 1.0)
        self.update_visible_width(visible_width)
        self.update_center(center)

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

    def as_dict(self):
        d = dict(self.others)
        d['editor_type_id'] = self.editor_type_id
        d['ingame_type_id'] = self.ingame_type_id
        d['visible_width'] = self.visible_width
        d['cx'] , d['cy'] = self.cshape.center
        return d

    def pprint(self):
        pprint.pprint(self.as_dict())

class LevelProxy(cocos.layer.ScrollableLayer):
    editor_type_id = 'levelproxy 00.01'

    @classmethod
    def new_from_dict(cls, game, description_dict):
        ingame_type_id = description_dict.pop('ingame_type_id')
        actor_variants = game['roles']['actor']
        actors = description_dict.pop('actors')
        width = description_dict.pop('width')
        height = description_dict.pop('height')
        others = description_dict
        level = LevelProxy(ingame_type_id, width, height, **others)
        z = 0
        for desc in actors:
            editor_type_id = desc.pop('editor_type_id')
            combo_type = (editor_type_id, desc['ingame_type_id'])
            # if needed, handle here editor versionning
            # ...
            assert combo_type in actor_variants
            actor = ActorProxy.new_from_dict(game, desc)
            level.add_actor(actor, z=z)
            z += 1

        return level

    def __init__(self, ingame_type_id, world_width, world_height, **others):
        super(LevelProxy, self).__init__()
        self.ingame_type_id = ingame_type_id
        # all measured in world units
        self.width = world_width
        self.height = world_height
        self.others = others
        self.px_width = world_width
        self.px_height = world_height
        self.maxz = -1

        self.batch = cocos.batch.BatchNode()
        self.add(self.batch)

        #actors
        self.actors = set()

    def on_enter(self):
        super(LevelProxy, self).on_enter()
        scroller = self.get_ancestor(cocos.layer.ScrollingManager)
        scroller.set_focus(self.width/2.0, self.height/2.0) 

    def add_actor(self, actor, z=None):
        self.actors.add(actor)
        if z is None:
            z = self.maxz + 1
        if z > self.maxz:
            self.maxz = z
        self.batch.add(actor, z=z)

    def remove_actor(self, actor):
        self.actors.remove(actor)
        self.batch.remove(actor)

    def as_dict(self):
        d = dict(self.others)
        d['editor_type_id'] = self.editor_type_id
        d['ingame_type_id'] = self.ingame_type_id
        d['width'] = self.width
        d['height'] = self.height
        zactors = list(self.batch.children)
        zactors.sort(key=operator.itemgetter(0))
        f = operator.itemgetter(1)
        d['actors'] = [ f(zactor).as_dict() for zactor in zactors ]
        return d

# el que conoce los available actors es game
def add_sample_actors_to_level(game, level_proxy):
    actor_types = game['roles']['actor']
    x0 = 400.0
    dx = 32.0
    i = 0
    for combo_type in actor_types:
        editor_type_id, ingame_type_id = combo_type
        assert editor_type_id == ActorProxy.editor_type_id
        params = actor_types[combo_type]
        img = params['editor_img']
        visible_width = params['visible_width']
        others = dict(params['others'])
        actor = ActorProxy(ingame_type_id, x0, x0, visible_width,
                           img, **others)
        level_proxy.add_actor(actor, z=i)
        i += 1
        x0 += 32
