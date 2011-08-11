import random
import operator
import pprint

import cocos
import cocos.euclid as eu
import cocos.collision_model as cm

fe = 1.0e-4

class Level(cocos.layer.ScrollableLayer):
    ingame_type_id = 'level 00.01'
    
    @classmethod
    def new_from_dict(cls, game, fn_cls_from_combo_type, args, description_dict):
        """
        don't modify, autority is editor

        args provides aditional positional arguments that must reach the
        __init__. These arguments don't come from the stored map, they are
        generated at game runtime just before calling here.
        Look at the manual for extra info

        description_dict carries the info for this instantiation comming
        from the stored level  
        """
        ingame_type_id = description_dict.pop('ingame_type_id')
        actors = description_dict.pop('actors')
        level = cls(*args, **description_dict)
        level.fill(game, fn_cls_from_combo_type, actors)
        return level

    def __init__(self,
                 # custom, provided at runtime
                 controller, wconsts,
                 # editor mandated, dont touch 
                 width=1200.0, height=1000.0, others={}):
        """
        Adding or removing parameters must follow special rules to not break
        load-store, look in the manual in secctions named 'Changing code'
        """
        super(Level, self).__init__()
        # all measured in world units
        self.width = width
        self.height = height
        self.others = others
        self.px_width = width
        self.px_height = height
        self.maxz = -1

        # handle 'provided at runtime'
        self.controller = controller
        self.add(controller)
        gsize = wconsts['collman_static_cell_width']
        self.collman_static = cm.CollisionManagerGrid(0.0, width, 0.0, height,
                                                      gsize, gsize)
        gsize = wconsts['collman_dynamic_cell_width']
        self.collman_dynamic = cm.CollisionManagerGrid(0.0, width, 0.0, height,
                                                      gsize, gsize)
        self.max_proximity_distance = wconsts["max_proximity_distance"]
        # store to pass consts to actors
        self.wconsts = wconsts
        
        # process 'others' if necesary
        #...
        
        self.batch = cocos.batch.BatchNode()
        self.add(self.batch)

        #some groups of actors
        self.enemies = []
        self.jewels = []

        self.schedule(self.update)

    def on_enter(self):
        super(Level, self).on_enter()
        scroller = self.get_ancestor(cocos.layer.ScrollingManager)
        scroller.set_focus(self.width/2.0, self.height/2.0)
        self.world_to_screen = scroller.pixel_to_screen
        self.screen_to_world = scroller.pixel_from_screen

    def world_to_screen(self, wx, wy):
        """
        returns (sx, sy)
        the conversion of (wx, wy) world coordinates to screen coordinates.
        placeholder, will be defined in on_enter 
        """
        pass

    def screen_to_world(self, sx, sy):
        """
        returns (wx, wy)
        the conversion of (sx, sy) screen coordinates to world coordinates.
        placeholder, will be defined in on_enter 
        """
        pass

    def add_actor(self, actor, z=None):
        if z is None:
            z = self.maxz + 1
        if z > self.maxz:
            self.maxz = z
        self.batch.add(actor, z=z)

    def remove_actor(self, actor):
        self.batch.remove(actor)


    def fill(self, game, fn_cls_from_combo_type, actors):
        """ on behalf of new_from_dict
            oportunity to feed args to actor cls if needed
            oportunity to add actors to diferrent containers in level
        """
        actor_variants = game['roles']['actor']
        z = 0
        for desc in actors:
            # -> don't modify this block, dont use *_type_id after the block:
            # remember they will change when you upgrade your classes
            _editor_type_id = desc['editor_type_id']
            _ingame_type_id = desc['ingame_type_id']
            combo_type = (_editor_type_id, _ingame_type_id)
            assert combo_type in actor_variants
            cls = fn_cls_from_combo_type(_editor_type_id, _ingame_type_id)
            # <- ends sensitive block
            args = [self]
            actor = cls.new_from_dict(game, args, desc)

            # procees the actor entering to level

            #   make it be draw
            self.add_actor(actor, z=z)

            class_name = cls.__name__ 
            #   additonal processing not common to all actors
            #   I'm using the class name as a sort of ingame role
            if class_name == 'Player':
                self.player = actor
                actor.set_consts(self.wconsts['player'])
                self.player.controller = self.controller
            elif class_name == 'Tree':                
                self.collman_static.add(actor)
                # to spice the visuals lets have variations in tree colors
                # as current protoeditor don't handles color for actors
                # lets asign a random lerp between two good colors
                actor.set_color_lerp_fraction(random.random())
            elif class_name == 'Jewel':
                self.jewels.append(actor)
            elif class_name == 'Exit':
                pass
            else:
                # enemies
                self.enemies.append(actor)
                if class_name == "EnemyWanderer":
                    actor.set_consts(self.wconsts["wanderer"])
            z += 1

    def update(self, dt):
        player = self.player
        # prepare collision data for the frame.
        self.update_collision_data()
        
        player.update(dt)
        for actor in self.enemies:
            actor.update(dt)

        # player vs dynamic actors collision - proximity checks 
        for actor, d in self.collman_dynamic.ranked_objs_near(player,
                                                self.max_proximity_distance):
            class_name = actor.__class__.__name__
            if d < fe:
                # declare touch
                pass
            elif class_name == 'EnemyWanderer' or class_name == 'EnemyChained':
                actor.player_near(d)
                

    def update_collision_data(self):
        # things in collman_static don't change pos or rx, ry so only
        # collman_dynamic should be updated
        collman = self.collman_dynamic
        collman.clear()
        collman.add(self.player)
        for actor in self.enemies:
            collman.add(actor)
        for actor in self.jewels:
            collman.add(actor)

