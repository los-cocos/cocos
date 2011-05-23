"""
Interactive test overlap for RectShape
Shows two rects, both green if no collision, both red if they collide
Theres always a rect selected
Key <tab> toggles the rectangle selection
Arrow keys move the selected rect
Keys '+' '-' rotates the selected rect
"""
import math

import pyglet
from pyglet.window import key
from pyglet.gl import *
import cocos
import cocos.collision_model as cm
import cocos.euclid as eu

w_width = 800
w_height = 600

bindings = {
    key.LEFT:'left',
    key.RIGHT:'right',
    key.UP:'up',
    key.DOWN:'down',
    key.PLUS:'rot+',
    key.MINUS:'rot-',
    key.TAB:'toggle_selection'
    }


class RectShape(object):
    def __init__(self, center, n1, n2, half_width, half_height):
        self.center = center
        self.n1 = n1
        self.n2 = n2
        self.hw = half_width
        self.hh = half_height

    def overlaps(self, other):
        # ovelap iff no one side in both rects separates
        separator = 2
        def gt(x):
            return x > separator
        def lt(x):
            return x < separator

        # we need to repeat same tests swaping self and other
        a = self
        b = other
        dc = b.center - a.center
        for i in xrange(2):
            # look projection by a.n1
            
            an1_dc = a.n1.dot(dc)
            # to separate, all b vertexes should be same side as b.center
            if an1_dc < 0.0:
                separator = -a.hw
                f_can_separate = lt
            else:
                separator = a.hw
                f_can_separate = gt

            an1_bhwbn1 = b.hw * a.n1.dot(b.n1)
            an1_bhhbn2 = b.hh * a.n1.dot(b.n2)

            # check can separate condition over each b vertex
            if (f_can_separate(an1_dc + an1_bhwbn1 + an1_bhhbn2) and
                f_can_separate(an1_dc + an1_bhwbn1 - an1_bhhbn2) and
                f_can_separate(an1_dc - an1_bhwbn1 + an1_bhhbn2) and
                f_can_separate(an1_dc - an1_bhwbn1 - an1_bhhbn2)
                ):
                    # separation verified
                    return False

            # look projection by a.n2
            
            an2_dc = a.n2.dot(dc)
            # to separate, all b vertexes should be same side as b.center
            if an2_dc < 0.0:
                separator = -a.hh
                f_can_separate = lt
            else:
                separator = a.hh
                f_can_separate = gt

            an2_bhwbn1 = b.hw * a.n2.dot(b.n1)
            an2_bhhbn2 = b.hh * a.n2.dot(b.n2)

            if (f_can_separate(an2_dc + an2_bhwbn1 + an2_bhhbn2) and
                f_can_separate(an2_dc + an2_bhwbn1 - an2_bhhbn2) and
                f_can_separate(an2_dc - an2_bhwbn1 + an2_bhhbn2) and
                f_can_separate(an2_dc - an2_bhwbn1 - an2_bhhbn2)
                ):
                    # separation verified
                    return False
                
            # swap roles
            a, b = b, a
            dc = -dc
        # no projection shows separation, hence overlaps
        return True

    def vertexes(self):
        res = [ self.center + self.hw * self.n1 + self.hh * self.n2,
                self.center - self.hw * self.n1 + self.hh * self.n2,
                self.center - self.hw * self.n1 - self.hh * self.n2,
                self.center + self.hw * self.n1 - self.hh * self.n2
            ]
        return res

##    def distance(self, other):
##        pass
##    
##    def near_than(self, other, near_distance):
##        pass
##
##    def minmax(self):
##        pass

class Rect(object):
    def __init__(self, cshape, color):
        self.cshape = cshape
        self.color = color
        self.angle = 0.0 #radians

class World(object):
    def __init__(self):
        self.fastness = 160.0
        self.angular_velocity = math.pi / 3.0
        self.colors = ['green', 'red']
        mid_x = w_width//2
        mid_y = w_height//2
        disp = 200.0
        r_width = 64.0 
        r_height = 128.0
        e1 = eu.Vector2(1.0, 0.0)
        e2 = eu.Vector2(0.0, 1.0)

        a_shape = RectShape(eu.Vector2(mid_x-disp, mid_y), e1, e2,
                        r_width/2.0, r_height/2.0)
        rect_a = Rect(a_shape, 'green')
        
        b_shape = RectShape(eu.Vector2(mid_x+disp, mid_y), e1, e2,
                           r_width/2.0, r_height/2.0)
        rect_b = Rect(b_shape, 'green')
        
        self.rects = [rect_a, rect_b]
        self.selected = 0
        self.toggle_pressed = False

    def toggle_selection(self):
        self.selected = 1 - self.selected

    def on_update(self, dt, buttons):
        update_view = False
        # toggle selection
        if buttons['toggle_selection']:
            if not self.toggle_selection_pressed:
                self.toggle_selection_pressed = True
                self.selected = 1 - self.selected
        else:
            self.toggle_selection_pressed = False

        mx = buttons['right'] - buttons['left'] 
        my = buttons['up'] - buttons['down']
        ma = buttons['rot+'] - buttons['rot-']
        if mx==0 and my==0 and ma==0:
            # no changes
            return
        update_view = True
        cshape = self.rects[self.selected].cshape
        # mov
        if mx != 0 or my != 0:
            fastness_dt = self.fastness*dt
            if mx != 0 and my != 0:
                fastness_dt *= 0.707106 # 1/sqrt(2)
            cshape.center += eu.Vector2(mx * fastness_dt, my * fastness_dt)
        # rot
        if ma != 0:
            a = self.rects[self.selected].angle + dt * ma * self.angular_velocity
            self.rects[self.selected].angle = a
            cosa = math.cos(a)
            sina = math.sin(a)
            cshape.n1 = eu.Vector2(cosa, sina)
            cshape.n2 = eu.Vector2(sina, -cosa)

        # set colors from collision
        if update_view:
            if self.rects[0].cshape.overlaps(self.rects[1].cshape):
                color = 'red'
            else:
                color = 'green'
            for rect in self.rects:
                rect.color = color

# view

class VertexBag(cocos.cocosnode.CocosNode):
    """ WARN: it is not a real CocosNode, it pays no attention to position,
        rotation, etc. It only draws the quad depicted by the vertexes.
        In other worlds, a nasty hack that gets the work done and you
        should not take as example"""
    def __init__(self):
        super(VertexBag, self).__init__()
        self.color3 = (0,0,255)
        self.vertexes = [ (0.0, 0.0) ] * 4

    def draw(self):
        glLineWidth(2) #deprecated
        glColor3ub(*self.color3)
        glBegin(GL_LINE_STRIP)
        for v in self.vertexes:
            glVertex2f(*v)
        glVertex2f(*self.vertexes[0])
        glEnd()

class ControllerLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, bindings):
        super(ControllerLayer, self).__init__()
        self.bindings = bindings
        buttons = {}
        for k in bindings:
            buttons[bindings[k]] = 0
        self.buttons = buttons

    def on_key_press(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False
        
def cocos_visualization():
    print """
    Interactive test overlap for RectShape
    Shows two rects, both green if no collision, both red if they collide
    Theres always a rect selected
    Key <tab> toggles the rectangle selection
    Arrow keys move the selected rect
    Keys '+' '-' rotates the selected rect
    """

    # prepare world
    world = World()
      
    # initialize cocos and prepare a scene to visualize world

    import cocos
    from cocos.director import director
    director.init(width=int(w_width), height=int(w_height), vsync=True)
    director.show_FPS = False

    scene = cocos.scene.Scene()
    model_to_view = {}
    for actor in world.rects:
        view_actor = VertexBag() 
        scene.add(view_actor)
        model_to_view[actor] = view_actor

    controller = ControllerLayer(bindings)
    scene.add(controller)
    def make_updater(world, model_to_view):
        def f(dt):
            world.on_update(dt, controller.buttons)
            for actor in world.rects:
                view_actor = model_to_view[actor]
                view_actor.vertexes = actor.cshape.vertexes()
                view_actor.color3 = { 'red':(255, 0, 0), 'green':(0, 255, 0)}[actor.color]
        return f

##    def make_updater(world, model_to_view):
##        def f(dt):
##            world.on_update(dt, controller.buttons)
##            for actor in world.actors:
##                view_actor = model_to_view[actor]
##                view_actor.position = actor.cshape.center
##                view_actor.rotation = math.degree(actor.angle)
##                view_actor.color3 = { 'red':(255, 0, 0), 'green':(0, 255, 0)}[actor.color]
##        return f

    mv_update = make_updater(world, model_to_view)
    controller.schedule(mv_update)
    scene.enable_handlers()

    # run
    director.run(scene)
    
cocos_visualization()
