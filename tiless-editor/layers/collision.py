"""
Layer for having collision detection.
"""
from __future__ import division
import os.path

import pymunk as pm
from pymunk.vec2d import Vec2d

from picker import PickerBatchNode

__all__ = ["Body", "Circle", "Segment", "Polygon", "CollisionSpace", "CollisionLayer"]

# FIXME: set better values for static bodies
STATIC_BODY_MASS = 1000
STATIC_BODY_INERTIA = 1000

def _get_vars(obj):
    return (x for x in dir(obj) if not x.startswith('_'))


class Body(object):
    def __init__(self, mass=STATIC_BODY_MASS, inertia=STATIC_BODY_INERTIA):
        self.mass = mass
        self.inertia = inertia


class Shape(object):
    def __init__(self, position=(0, 0), scale=1.0, rotation=0, body=None):
        if body is None:
            body = Body()

        self._position = position
        self._scale = scale
        self._rotation = rotation
        self.body = body

    @apply
    def position():
        def fget(self):
            return self._position
        def fset(self, position):
            old_position = self._position
            self._position = position
            offset = Vec2d(position) - Vec2d(old_position)
            # update position sensible attributes
            self._position_updated(offset)
        return property(fget, fset)

    @apply
    def scale():
        def fget(self):
            return self._scale
        def fset(self, scale):
            old_scale = self._scale
            self._scale = scale
            factor = scale / old_scale
            # update scale sensible attributes
            self._scale_updated(factor)
        return property(fget, fset)

    @apply
    def rotation():
        def fget(self):
            return self._rotation
        def fset(self, rotation):
            old_rotation = self._rotation
            self._rotation = rotation
            angle = rotation - old_rotation
            # update rotation sensible attributes
            self._rotation_updated(angle)
        return property(fget, fset)

    def _position_updated(self, offset):
        pass

    def _scale_updated(self, factor):
        pass

    def _rotation_updated(self, angle):
        pass


class Circle(Shape):
    def __init__(self, radius, position=(0, 0), scale=1.0, rotation=0):
        super(Circle, self).__init__(position, scale, rotation)
        self.radius = radius

    def _scale_updated(self, factor):
        self.radius *= factor

    def draw(self):
        import shape
        x, y = self.position
        width = height = self.radius * 2
        rotation = -self.rotation
        _shape = shape.Ellipse(x=x, y=y,
                               width=width, height=height,
                               rotation=rotation,
                               anchor_x='center', anchor_y='center')
        _shape.draw()


class Segment(Shape):
    def __init__(self, radius, length, position=(0, 0), scale=1.0, rotation=0):
        super(Segment, self).__init__(position, scale, rotation)
        self.radius = radius
        self.length = length

    def _scale_updated(self, factor):
        self.radius *= factor
        self.length *= factor

    def draw(self):
        import shape
        x, y = self.position
        width = self.length
        height = self.radius * 2
        rotation = -self.rotation
        _shape = shape.Ellipse(x=x, y=y,
                               width=width, height=height,
                               rotation=rotation,
                               anchor_x='center', anchor_y='center')
        _shape.draw()


class Polygon(Shape):
    def __init__(self, vertices, position=(0, 0), scale=1.0, rotation=0):
        super(Polygon, self).__init__(position, scale, rotation)
        self.vertices = vertices

    def _position_updated(self, offset):
        self._update_vertices(offset)

    def _scale_updated(self, factor):
        self._update_vertices(factor=factor)

    def _rotation_updated(self, angle):
        self._update_vertices(angle=angle)

    def _update_vertices(self, offset=(0, 0), scaling_factor=1.0, rotation_angle=0):
        for i in xrange(len(self.vertices)):
            self.vertices[i] += Vec2d(offset)
            self.vertices[i].length *= scaling_factor


class Square(Polygon):
    def __init__(self, width, height, position=(0, 0), scale=1.0, rotation=0):
        vertices = self._generate_vertices(width, height, position)
        super(Square, self).__init__(vertices, position, scale, rotation)
        self.width = width
        self.height = height

    def _position_updated(self, offset):
        self._rebuild_vertices()

    def _scale_updated(self, factor):
        self.width *= factor
        self.height *= factor
        self._rebuild_vertices()

    def _rotation_updated(self, angle):
        self._rebuild_vertices()

    def _rebuild_vertices(self):
        self.vertices = self._generate_vertices(self.width, self.height,
                                                self.position, self.scale,
                                                self.rotation)

    def _generate_vertices(self, width, height, position=(0, 0), scale=1.0, rotation=0):
        _height = Vec2d(0, height) * 0.5
        _width = Vec2d(width, 0) * 0.5
        position = Vec2d(position)
        v1 = position +  _height - _width
        v2 = position -  _height - _width
        v3 = position -  _height + _width
        v4 = position +  _height + _width
        # FIXME: take rotation into account when generating vertices
        vertices = [v1, v2, v3, v4]
        return vertices

    def draw(self):
        import shape
        x, y = self.position
        width = self.width
        height = self.height
        rotation = -self.rotation
        _shape = shape.Rectangle(x=x, y=y,
                                 width=width, height=height,
                                 rotation=rotation,
                                 anchor_x='center', anchor_y='center')

        pos = Vec2d(x, y)
        _shape_vertices = _shape.generate_vertices()[0]
        #print 'Square:'
        #print 'position: ', self.position
        #print 'width, height ', self.width, self.height
        #print 'vertices: ', self.vertices
        #print 'shape_vertices: ', _shape_vertices
        _shape.draw()


class CollisionSpace(object):
    """
    A layer that provides collision detection between shapes, using
    pymunk as the 2d physics simulation engine.
    """

    # FIXME: is this the best way to declare the minimal amount
    # of time for the collision detection to work when physics are
    # not enabled?
    DELTA_T = 0.000000000000001

    def __init__(self, callback=None, physics=False):
        pm.init_pymunk()

        self._space = pm.Space()
        # for now, we just use a single generic collision handler
        self._space.set_default_collisionpair_func(self._on_collide)
        self._active_objects = {}
        self._static_objects = {}

        # this is the callback we call when a collision has happened
        self.callback = callback
        self.physics = physics

    def add(self, child, static=False):
        obj = self._get_or_create_pm_object(child, static)
        if static:
            self._static_objects[child] = obj
            self._space.add_static(obj)
        else:
            self._active_objects[child] = obj
            self._space.add(obj)
            self._space.add(obj.body)

    def remove(self, child, static=False):
        obj = self._get_pm_object(child, static)

        if obj is not None:
            if static:
                self._space.remove_static(obj)
                objects = self._static_objects
            else:
                self._space.remove(obj.body)
                self._space.remove(obj)
                objects = self._active_objects
            del objects[child]

    def step(self, dt=0):
        if not self.physics:
            # clean up forces from previous iterations
            self._reset()
            # for collision detection we just need to run the physics simulation
            # without increasing the virtual time
            dt = self.DELTA_T
        # run the simulation, in order to trigger the collision detection
        self._space.step(dt)

    def _get_or_create_pm_object(self, obj, static=False):
        pm_obj = self._get_pm_object(obj, static)
        if pm_obj is None:
            pm_obj = self._create_pm_object(obj)

        return pm_obj

    def _get_pm_object(self, obj, static=None):
        pm_obj = None
        if static is None:
            pm_obj = self._active_objects.get(obj)
            if pm_obj is None:
                pm_obj = self._static_objects.get(obj)
        else:
            if static:
                objects = self._static_objects
            else:
                objects = self._active_objects
            pm_obj = objects.get(obj)

        return pm_obj

    def _create_pm_object(self, shape):
        mass = shape.body.mass
        inertia = shape.body.inertia
        pm_body = pm.Body(mass, inertia)
        pm_body.position = shape.position

        if isinstance(shape, Circle):
            radius = shape.radius
            # WARNING: for now, circle shapes are completely aligned to their
            # body's center of gravity
            offset = (0, 0)
            pm_obj = pm.Circle(pm_body, radius,  offset)
        elif isinstance(shape, Segment):
            # WARNING: the segment is assumed to be centered around its position
            # points a and b are equally distant from the segments center
            position = Vec2d(shape.position)
            length = Vec2d(shape.length, 0)
            a = position - 0.5 * length
            b = position + 0.5 * length
            radius = shape.radius
            pm_obj = pm.Segment(pm_body, a, b, radius)
        elif isinstance(shape, Polygon):
            vertices = shape.vertices
            # WARNING: for now, polygon shapes are completely aligned to their
            # body's center of gravity
            offset = (0, 0)
            pm_obj = pm.Poly(pm_body, vertices, offset)

        return pm_obj

    def _on_collide(self, pm_shapeA, pm_shapeB, contacts, normal_coef, data):
        if self.callback is not None:
            shapeA = self._get_shape(pm_shapeA)
            shapeB = self._get_shape(pm_shapeB)
            self.callback(shapeA, shapeB)
        return True

    def _get_shape(self, pm_shape):
        for objects in (self._active_objects, self._static_objects):
            for k, v in objects.items():
                if v == pm_shape:
                    return k
        raise KeyError("Requested a non-existing shape. Data corruption" 
            "possible.")

    def _reset(self):
        for body in self._space.bodies:
            body.reset_forces()

    def update(self, shape):
        pm_obj = self._get_pm_object(shape)
        if pm_obj is not None:
            for attr in _get_vars(shape):
                if attr == 'body':
                    # special case: the 'body' attribute has to be exploded
                    # further
                    for body_attr in _get_vars(shape.body):
                        value = getattr(shape.body, body_attr)
                        setattr(pm_obj.body, body_attr, value)
                elif attr == 'position':
                    # special case: the 'position' attribute is special,
                    # because it is located at the top level in the source
                    # object and inside the 'body' attribute of the pymunk
                    # object
                    value = getattr(shape, attr)
                    setattr(pm_obj.body, attr, value)
                else:
                    value = getattr(shape, attr)
                    setattr(pm_obj, attr, value)

        if self.is_static(shape):
            # since a static shape has been moved, we need to rehash them
            self._space.rehash_static()

    def is_static(self, shape):
        return self._static_objects.has_key(shape)


class CollisionLayer(PickerBatchNode):
    def __init__(self, callback=None):
        super(CollisionLayer, self).__init__()

        self._shapes = {}
        self.show_shapes = False
        if callback is None:
            callback = self._on_collision
        self.space = CollisionSpace(callback=callback)

    def add(self, child, z=0, name=None, static=True):
        super(CollisionLayer, self).add(child, z, name)

        # create a shape
        shape = self._create_shape(child)
        self.space.add(shape, static)
        self._shapes[child] = shape

    def remove(self, obj, static=True):
        shape = self._shapes[obj]
        self.space.remove(shape, static)
        del self._shapes[obj]
        super(CollisionLayer, self).remove(obj)

    def on_notify(self, node, attribute):
        shape = self._shapes[node]
        value = getattr(node, attribute)
        setattr(shape, attribute, value)
        self.space.update(shape)
        super(CollisionLayer, self).on_notify(node, attribute)

    def visit(self):
        super(CollisionLayer, self).visit()
        if self.show_shapes:
            # used for debugging purposes
            self._show_shapes()

    def step(self, dt=0):
        self.space.step(dt)

    def _create_shape(self, child):
        def get_shape_name(child):
            image_name = os.path.basename(child.path)
            shape_name = image_name.split('.')[0]
            return shape_name

        _shape = get_shape_name(child)
        if _shape == 'circle':
            radius = 0.5 * max(child.width, child.height)
            shape = Circle(radius, child.position, child.scale, child.rotation)
        elif _shape == 'segment':
            radius = 0.5 * child.height
            length = child.width
            shape = Segment(radius, length, child.position, child.scale, child.rotation)
        elif _shape == 'square':
            shape = Square(child.width, child.height, child.position, child.scale, child.rotation)
        else:
            raise ValueError("Child has invalid shape", _shape)

        return shape

    #################
    # Helper methods (for debugging collisions)
    #################
    def  _on_collision(self, shape_a, shape_b):
        # this is a default implementation for the callback
        # it shows the shapes that collided in a visual way
        self._alert(shape_a)
        self._alert(shape_b)

    def _get_node(self, shape):
        for k, v in self._shapes.iteritems():
            if v == shape:
                return k

    def _alert(self, shape):
        from cocos.actions import ScaleBy, Reverse
        node = self._get_node(shape)
        if node is not None:
            scale = ScaleBy(2,1.5)
            scale_back = Reverse(scale)
            node.do(scale + scale_back)

    def _show_shapes(self):
        from pyglet.gl import glPushMatrix, glPopMatrix
        glPushMatrix()
        self.transform()
        for shape in self._shapes.values():
            # draw each shape
            shape.draw()
        glPopMatrix()
