"""
        This script has two purposes:

            Allow to benchmark different collision managers

            Have a ballpark number for the framerate attainable when moving and
            checking actors collisions, when all actors are visible.

        Note that this is a good case, in the sense that the actors don't
        concentrate in small zones of the world.

        Finally, for accurate physics simulation I would go with a 2D physics
        engine, like pymunk or box2D
"""

from __future__ import division, print_function, unicode_literals

import random
import time
import math


import cocos.euclid as eu
# the cocos.collision_model implementation to test is imported elsewhere and
# stored in __builtins__.collision_module

fe = 1.0e-4

class Ball(object):        
    def __init__(self, cshape, velocity):
        self.cshape = cshape
        self.vel = velocity
        self.accel = eu.Vector2(0.0, 0.0)
        self.colliding = False


def get_ball_maker(cshape_cls_name, radius):
    def with_CircleShape(center, velocity):
        cshape = collision_module.CircleShape(center, radius)
        return Ball(cshape, velocity)

    def with_AARectShape(center, velocity):
        rx = 0.8 * radius
        cshape = collision_module.AARectShape(center, rx, rx)
        return Ball(cshape, velocity)
    
    if cshape_cls_name == 'CircleShape':
        return with_CircleShape
    elif cshape_cls_name == 'AARectShape':
        return with_AARectShape
    else:
        print("\n Error, unknown cshape class name:", cshape_cls_name)


class World(object):
    def __init__(self, world_width=0, world_height=0, border_thickness=0,
                 ball_radius=0, fastness=0, k_border=0, k_ball=0,
                 cshape_cls_names=[], collision_manager=0):
        # all parameters are required, default values are set only to allow
        # call with **kwargs
        self.width = world_width
        self.height = world_height
        self.border_thickness = border_thickness
        self.ball_radius = ball_radius
        self.fastness = fastness
        self.k_border = k_border
        self.k_ball = k_ball
        self.fn_ball_makers = [get_ball_maker(name, ball_radius)
                                                   for name in cshape_cls_names]
        self.num_cshapeclasses = len(cshape_cls_names)
        self.collman = collision_manager

        self.actors = []
        self.x_lo = border_thickness + ball_radius
        self.x_hi = world_width - border_thickness - ball_radius
        self.y_lo = border_thickness + ball_radius
        self.y_hi = world_height - border_thickness - ball_radius

    def set_actor_quantity(self, n):
        random_uniform = random.uniform
        pi2 = 2*math.pi
        for i in range(n):
            x = random_uniform(self.x_lo, self.x_hi)
            y = random_uniform(self.y_lo, self.y_hi)
            a = random_uniform(0.0, pi2)
            vel = self.fastness * eu.Vector2(math.cos(a), math.sin(a))
            k = i % self.num_cshapeclasses
            actor = self.fn_ball_makers[k](eu.Vector2(x, y), vel)
            self.actors.append(actor)
            try:
                self.collman.add(actor)
            except:
                print('ex in add; pos: %7.3f , %7.3f'%(actor.cshape.center[0],
                                                       actor.cshape.center[1]))
        print('*** end adding actors')


    def update(self, dt):
        r = self.ball_radius
        x_lo = self.x_lo
        x_hi = self.x_hi
        y_lo = self.y_lo
        y_hi = self.y_hi
        k_border = self.k_border
        k_ball = self.k_ball

        # acceleration, contribution of world bounce box
        for actor in self.actors:
            x, y = actor.cshape.center
            accel = eu.Vector2(0.0, 0.0)
            if x < x_lo:
                accel += eu.Vector2(-k_border * (x - x_lo), 0.0)
            elif x > x_hi:
                accel += eu.Vector2(-k_border * (x - x_hi), 0.0)
            if y < y_lo:
                accel += eu.Vector2(0.0, -k_border * (y - y_lo))
            elif y > y_hi:
                accel += eu.Vector2(0.0, -k_border * (y - y_hi))
            actor.accel = accel

        # acceleration, contribution by actors collisions
        double_r = 2*r
        for actor, other in self.collman.iter_all_collisions():
            delta = actor.cshape.center - other.cshape.center
            d = delta.magnitude()
            if d<fe:
                continue
            accel = k_ball*(double_r - d)*delta/d
            actor.accel += accel
            other.accel -= accel
            actor.colliding = True
            other.colliding = True
            
        # dt step
        for actor in self.actors:
            dv = dt * actor.accel
            actor.cshape.center += dt * (actor.vel + 0.5 * dv)
            actor.vel += dv
            if actor.colliding and actor.accel == eu.Vector2(0.0, 0.0):
                actor.vel = self.fastness * actor.vel.normalized()
                actor.colliding = False

        # update collman
        if not isinstance(self.collman, collision_module.CollisionManagerBruteForce):
            add = self.collman.add
            self.collman.clear()
            for actor in self.actors:
                add(actor)


    
def cocos_visualization():
    print("""
        This script has two purposes:

            Allow to benchmark different collision managers

            Have a ballpark number for the framerate attainable when moving and
            checking actors collisions, when all actors are visible.

        Note that this is a good case, in the sense that the actors don't
        concentrate in small zones of the world.

        Finally, for accurate physics simulation I would go with a 2D physics
        engine, like pymunk or box2D
        """)

    # instantiate and fill World
    world_params = {
        'seed': 123456,
        'world_width': 800.0,
        'world_height': 600.0,
        'border_thickness': 50.0, 
        'ball_radius': 16.0,
        'fastness': 64.0,
        'k_border': 10.0,
        'k_ball': 10.0,
        
        'cshape_cls_names': ['CircleShape', 'AARectShape'],
        'collision_manager': None # must be filled, see below
        }
    ball_quantity = 40 # 175 # 300

    random.seed(world_params.pop('seed'))
    cell_side = world_params['ball_radius'] * 2.0
    collman = collision_module.CollisionManagerGrid(0.0, world_params['world_width'],
                                      0.0, world_params['world_height'],
                                      cell_side, cell_side)
    world_params['collision_manager'] = collman
    world = World(**world_params)
    world.set_actor_quantity(ball_quantity)
      
    # initialize cocos and prepare a scene to visualize world

    import cocos
    from cocos.director import director
    director.init(width=int(world.width), height=int(world.height), vsync=False)
    director.show_FPS = True

    scene = cocos.scene.Scene()
    scene.batch = cocos.batch.BatchNode()
    scene.add(scene.batch)
    no_border = cocos.layer.ColorLayer(34, 32, 180, 255,
                            width=int(world.width-2*world.border_thickness),
                            height=int(world.height-2*world.border_thickness))
    no_border.position = int(world.border_thickness), int(world.border_thickness)
    scene.add(no_border, z=-1)
    model_to_view = {}
    for actor in world.actors:
        sp = cocos.sprite.Sprite('ball32.png')
        sp.scale = 2.0 * world.ball_radius / sp.width
        scene.batch.add(sp)
        model_to_view[actor] = sp

    def make_updater(world, model_to_view):
        def f(dt):
            world.update(dt)
            for actor in world.actors:
                model_to_view[actor].position = actor.cshape.center 
        return f

    mv_update = make_updater(world, model_to_view)
    scene.schedule(mv_update)
    scene.enable_handlers()

    # run
    director.run(scene)


if __name__=='__main__':
    import cocos.collision_model as cm
    __builtins__.collision_module = cm
    cocos_visualization()

