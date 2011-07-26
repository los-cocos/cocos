import operator

import cocos
import cocos.euclid as eu
import cocos.collision_model as cm

class ActorProxy(cocos.sprite.Sprite):
    editor_type_id = 'ActorProxy 00.01'

    @classmethod
    def new_from_dict(cls, description_dict):
        desc = description_dict
        ingame_type_id = desc.pop('ingame_type_id')
        editor_img = game['available_actor_types'][ingame_type_id]['editor_img']
        cx = desc.pop('cx')
        cy = desc.pop('cy')
        visible_width = desc.pop('visible_width')
        actor = ActorProxy(ingame_type_id, cx, cy, visible_width,
                           editor_img, **desc)
        return actor

    def __init__(self, ingame_type_id, cx, cy, visible_width,
                 ed_image, **others):
        super(ActorProxy, self).__init__(ed_image)
        self.ingame_type_id = ingame_type_id
        # measured in world units
        self.visible_width = visible_width
        self.others = others
        self.scale =  float(visible_width) / self.width
        rx = visible_width / 2.0
        ry = self.height / 2.0 * self.scale
        center = eu.Vector2(cx, cy)
        self.cshape = cm.AARectShape(center, rx, ry)
        self.update_center(center)

    def update_center(self, new_center):
        assert isinstance(new_center, eu.Vector2) 
        self.position = new_center
        self.cshape.center = new_center

    def as_dict(self):
        d = dict(self.others)
        d['editor_type_id'] = self.editor_type_id
        d['ingame_type_id'] = self.ingame_type_id
        d['visible_width'] = self.visible_width
        d['cx'] , d['cy'] = self.cshape.center
        return d

    def pprint(self):
        # useful when using the interactive interpreter
        pass

class LevelProxy(cocos.layer.ScrollableLayer):
    editor_type_id = 'LevelProxy 00.01' # here vs refers to ed proxy version

    @classmethod
    def new_from_dict(cls, description_dict):
        actors = description_dict.pop('actors')
        width = description_dict.pop('width')
        height = description_dict.pop('height')
        others = description_dict
        level = LevelProxy(width, height, **others)
        z = 0
        for desc in actors:
            editor_type_id = desc.pop('editor_type_id')
            # if needed, handle here editor versionning
            # ...
            assert editor_type_id == ActorProxy.editor_type_id
            actor = ActorProxy.new_from_dict(desc)
            level.add_actor(actor, z=z)
            z += 1

        return level

    def __init__(self,
                 world_width, world_height, **others):
        super(LevelProxy, self).__init__()
        # all measured in world units
        self.width = world_width
        self.height = world_height
        self.others = others
        self.px_width = world_width
        self.px_height = world_height

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
        self.batch.add(actor, z=z)

    def remove_actor(self, actor):
        self.actors.remove(actor)
        self.batch.remove(actor)

    def as_dict(self):
        d = dict(self.others)
        d['editor_type_id'] = self.editor_type_id
        d['width'] = self.width
        d['height'] = self.height
        zactors = list(self.batch.children)
        zactors.sort(key=operator.itemgetter(0))
        f = operator.itemgetter(1)
        d['actors'] = [ f(zactor).as_dict() for zactor in zactors ]
        return d

# el que conoce los available actors es game
from gamedef import game
def add_sample_actors_to_level(level_proxy):
    actor_types = game['available_actor_types']
    x0 = 400.0
    dx = 32.0
    i = 0
    for actor_type_descriptor in actor_types:
        params = actor_types[actor_type_descriptor]
        img = params['editor_img']
        visible_width = params['visible_width']
        others = dict(params['others'])
        actor = ActorProxy(actor_type_descriptor, x0, x0, visible_width,
                           img, **others)
        level_proxy.add_actor(actor, z=i)
        i += 1
        x0 += 32
