import operator
import pprint
import random
from math import radians, sin, cos, pi


import cocos
import cocos.euclid as eu
import cocos.collision_model as cm
import cocos.actions as ac
fe = 1.0e-4

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

    def set_consts(self, consts):
        self.max_fastness = consts['max_fastness']
        self.accel = consts['accel']
        # not proper, but short. Move to init when overriden
        self.vel = eu.Vector2(0.0, 0.0)
        self.heading = eu.Vector2(0.0, 1.0)
        self.fastness = 0.0

    def on_enter(self):
        super(Player, self).on_enter()
        self.scroller = self.get_ancestor(cocos.layer.ScrollingManager)

    def update(self, dt):
        buttons = self.controller.buttons
        mx = (buttons['right'] - buttons['left'])
        my = (buttons['up'] - buttons['down'])
        old_vel = self.vel
        if mx!=0 or my!=0:
            vel = old_vel + (dt * self.accel )* eu.Vector2(mx, my)
            fastness = vel.magnitude()
            if fastness > fe:
                self.heading = vel / fastness
            if fastness > self.max_fastness:
                vel = self.heading * self.max_fastness
            self.vel = vel
        # chopiness with pyglet 1.1.4 release, looks right with 1.2dev
        # I see dt more inestable with 1.1.4, even if fps ~57-60 with vsync
        # I know there have been code changes related to dt, also the pyglet
        # issue tracker shows a report about dt instability with some ATI
        # divers which can apply here. I will not upgrade just now, must be
        # further investigated

        # simpler, more sensitive to irregular dt, looks right with pyglet 1.2dev 
        new_pos = self.cshape.center + dt * self.vel

        # teoricaly more stable with dt variations, at least when accelerating
        # paralell to the axis, but remains chopy with pyglet 1.1.4
        #new_pos = self.cshape.center + dt * (old_vel + (0.5 * dt * self.accel) * self.heading)

        # new_pos not clamped, maps should protect the borders with trees
        self.update_center(new_pos)

        # this should be upgraded to something like the autoscroll in protoeditor
        # but that should probably wait till the fix for scroller intifier prob.
        self.scroller.set_focus(*new_pos)
        

class EnemyWanderer(BaseActor):
    """
    The most simplest behavior. (im late to release deadline)
    The bot has two states:
        wandering : choses a random direction, walks in that direction,
                    if it sees player changes to the state chasing
        chasing : walk heading to the current player position, if player goes
                  out of sight change to state wandering

    The states would update heading and maybe fastness, which will be used
    by update_position
    ---
    Downgrade: no time to code 'can see player', reduced the chasing
    distances, pretending enemies are near blind 
    ---
    Assumptions:
    Initial position don't collides with a tree
    level surrounded by trees, ie no need to check world boundaries
    """
    ingame_type_id = 'wanderer 00.01'

    def __init__(self, *args, **kwargs):
        super(EnemyWanderer, self).__init__(*args, **kwargs)
        self.state = None
        self.last_not_colliding = self.cshape.center

    def set_consts(self, consts):
        self.max_wandering_fastness = consts['max_wandering_fastness'] 
        self.min_wandering_fastness = consts['min_wandering_fastness'] 
        self.chasing_fastness = consts['chasing_fastness']
        self.start_chase_distance = consts["start_chase_distance"]
        self.end_chase_distance = consts['end_chase_distance']
        # next line cant go in init (would fail but not having the consts)
        self.go_state('wandering', False)

    def go_state(self, state, *args):
        print 'entering state:', state
        getattr(self, 'enter_' + state)(*args)
        self.state = state
        self.update_state = getattr(self, 'e_' + state)

    def update_state(self):
        """
        Placeholder code. Will be replaced by go_state with one of the
        e_* functions, which must have the same signature as this placeholder.
        """
        pass

    def enter_wandering(self, after_tree_collision):
        """
        chose a random direction to start to walk
        set fastness goal as max_wandering_fastness. A bit of random here ?  
        """
        # try to find a good random heading, then set vel  
        probe_distance = 16.0
        probe_slack_distance = 16.0
        self.fastness = random.uniform(self.max_wandering_fastness,
                                       self.min_wandering_fastness)
        collman = self.level.collman_static
        old_center = self.cshape.center
        a = random.uniform(0.0, 2*pi)
        da = 2 * pi / 5.0
        for i in xrange(5):
            heading = eu.Vector2(cos(a), sin(a))
            self.cshape.center = old_center + probe_distance * heading
            if not collman.any_near(self, probe_slack_distance):
                break
            a += da
        self.cshape.center = old_center
        self.heading = heading
        self.vel = self.fastness * heading

        # ignore player some time if collided a tree while chasing
        if after_tree_collision and self.state == 'chasing':
            self.player_near = self.player_near_ignore
            self.do(ac.Delay(1.0) + ac.CallFunc(self.end_ingnoring_player))
        else:
            self.player_near = self.player_near_wandering

    def end_ingnoring_player(self):
        self.player_near = self.player_near_wandering
        

    def e_wandering(self):
        """
        nothing to do currently
        """
        pass

    def enter_chasing(self):
        """
        set fastness goal as max_chasing_fastness
        """
        self.fastness = self.chasing_fastness
        self.player_near = self.player_near_chasing

    def e_chasing(self):
        """
        nothing to do currently
        """
        pass

    def player_near(self, d):
        """
        called by level if d=distance to player less than a threhold
        Placeholder code - will be replaced by player_near_* as needed
        """
        pass

    def player_near_chasing(self, d):
        if d > self.end_chase_distance:
            self.go_state('wandering', False)
        else:
            self.heading = (self.level.player.cshape.center -
                            self.cshape.center).normalized()
            self.vel = self.fastness * self.heading

    def player_near_wandering(self, d):
        if d < self.start_chase_distance:
            self.go_state('chasing')

    def player_near_ignore(self, d):
        pass

    def update(self, dt):
        old_pos = self.cshape.center 
        self.update_center(old_pos + dt * self.vel)
        if self.level.collman_static.any_near(self, fe):
            # touching a tree
            self.update_center(old_pos)
            self.go_state('wandering', True)

        self.update_state()



class EnemyChained(BaseActor):
    """
    Same as wanderer, but don't moves away of it spawn point
    more than certain distance
    """
    ingame_type_id = 'chained mons 00.01'

    def update(self, dt):
        pass

    def player_near(self, d):
        """
        called by level if d=distance to player less than a threhold
        Placeholder code - will be replaced by player_near_* as needed
        """
        pass

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
    
