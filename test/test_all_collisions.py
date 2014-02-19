from __future__ import division, print_function, unicode_literals

# a test scene used to help develop collision code for cocos.

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "f 10 0.033, s, f 20 0.033, s, f 30 0.033, s, f 30 0.033, s, q"
tags = "collision"

import cocos
from cocos.director import director
import cocos.actions as ac
import cocos.collision_model as cm
import cocos.euclid as eu

import random


# the driver parameters for the city view
# all city dimensions as integer multiples of half_street_width
half_street_width = 15
streets_per_side = 5 # first and last will be out of view
street_to_square_width_multiplier = 4

street_color = (170,170,0,255)
square_color = (120,32,120,255)

pool_car_size = 4
time_to_next_crossing = 1.0

# interesting city view quantities, derived from driver parameters and
# desired view
squares_per_side = streets_per_side - 1
street_width = 2*half_street_width
square_width = street_to_square_width_multiplier * street_width
# crossing points are at the center of street crossings, so
crossing_point_separation = square_width + 2*(half_street_width)

# we want the center of bottom left square at bottom left window, and the
# city view simetrical, so left to right in the x direction we see
# half square, [a street, a square] (repeat squares_per_side - 2 times), a
# street and half a square
view_width = ( 2*0.5*square_width + square_width*(squares_per_side -2) +
               street_width*(streets_per_side-2) )
view_width = square_width * (squares_per_side -1) + street_width*(streets_per_side-2)
view_height = view_width

# the distance in one dimension from a crossing to the center of next left
# square
offset = 0.5 * street_width + 0.5 * square_width
offset = half_street_width + street_to_square_width_multiplier * half_street_width
offset = half_street_width * (street_to_square_width_multiplier + 1)


class Actor(cocos.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        """same params as Sprite plus kwargs
                'rx', 'ry' for collision cshape
                'desired_width' """
        rx = kwargs.pop('rx', None)
        ry = kwargs.pop('ry', None)
        desired_width = kwargs.pop('desired_width', None)
        super(Actor, self).__init__(*args, **kwargs)
        if desired_width is None:
            desired_width = self.image.width
        desired_width = float(desired_width)
        self.scale =  desired_width / self.width
        if rx is None:
            rx = 0.8 * desired_width / 2.0
        if ry is None:
            ry = 0.8 * self.image.height / self.image.width * desired_width / 2.0
        #self.cshape = cm.AARectShape(eu.Vector2(0.0, 0.0), rx, ry)
        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), rx)#, ry)

    def update_position(self, new_position):
        assert isinstance(new_position, eu.Vector2)
        self.position = new_position
        self.cshape.center = new_position

class RobotCar(Actor):
    """
    """
    def __init__(self):
        super(RobotCar, self).__init__("circle6.png", desired_width=32)
        self.e_free()

    def e_free(self):
        self.state = 'free'
        self.color = ( 20, 120, 70)

    def e_burn(self):
        self.state = 'burning'
        self.color = (180, 0, 0)
        template_action = ac.Delay(2.0) + ac.CallFunc(self.e_free)
        self.do(template_action)

    def e_travel(self):
        self.state = 'traveling'

    def do_travel(self, initial_crossing, final_crossing):
        self.e_travel()
        self.color = ( 20, 120, 70)
        self.next_crossing = initial_crossing
        self.final_crossing = final_crossing
        self.update_when_crossing_reached()

    def update_when_crossing_reached(self):
        # set position exactly at old crossing
        ix, iy = self.next_crossing
        self.update_position(eu.Vector2(ix*crossing_point_separation,
                                        iy*crossing_point_separation))

        # update next_crossing
        dx = self.final_crossing[0] - self.next_crossing[0]
        ok = False
        # try to reduce error in x
        if dx!=0:
            dy = 0
            if dx < 0: dx = -1
            else: dx = 1
            ix += dx
            # it is not acceptable going invisible except if final crossing
            ok = ((0<ix<(streets_per_side-1) and (0<iy<streets_per_side-1)) or
                          ((ix, iy)==self.final_crossing))
            if not ok:
                ix -= dx

        if not ok:
            # reduce error in y
            dx = 0
            dy = self.final_crossing[1] - self.next_crossing[1]
            if dy!=0:
                if dy < 0: dy = -1
                else: dy = 1
                iy += dy
        self.next_crossing = ix, iy

        # now refresh params used to update position between crossings
        self.elapsed = 0.0
        self.arrival = time_to_next_crossing
        self.move_in_x = (dx!=0)
        fastness = crossing_point_separation / time_to_next_crossing
        if self.move_in_x:
            self.scalar_vel = dx * fastness
        else:
            self.scalar_vel = dy * fastness

    def is_travel_completed(self):
        return ((self.elapsed > self.arrival) and
                (self.next_crossing == self.final_crossing))

    def update(self, dt):
        """
        dont call this when self.state != 'traveling'
        """
        self.elapsed += dt
        if self.elapsed > self.arrival:
            # crossing reached
            if self.next_crossing == self.final_crossing:
                # travel finished
                self.e_free()
            else:
                self.update_when_crossing_reached()
        else:
            x, y = self.cshape.center
            # between crossings
            if self.move_in_x:
                x += self.scalar_vel*dt
            else:
                y += self.scalar_vel*dt
            self.update_position(eu.Vector2(x,y))


class City(cocos.layer.Layer):
    def __init__(self):
        super(City, self).__init__()
        bg = cocos.layer.ColorLayer(*street_color,width=view_width,
                                    height=view_width)
        self.add(bg)
        self.add_squares()
        self.position = -offset, -offset
        bg.position = offset, offset
        self.cars = set()
        while len(self.cars) < pool_car_size:
            car = RobotCar()
            self.cars.add(car)
            self.add(car)
        self.collman = cm.CollisionManagerGrid(-square_width, view_width + square_width,
                                               -square_width, view_height + square_width,
                                               40.0, 40.0)
        self.schedule(self.update)

    def add_squares(self):
        for iy in range(squares_per_side):
            y = half_street_width + iy*crossing_point_separation
            for ix in range(squares_per_side):
                square = cocos.layer.ColorLayer(*square_color,width=square_width,
                                    height=square_width)
                x = half_street_width + ix*crossing_point_separation
                square.position = (x,y)
                self.add(square, z=2)

    def generate_travel(self):
        #ix,iy : ints, street crossing; 0,0 is bottom left (out of view)
        #ix, iy maps to x,y = ix*crossing_point_separation + iy*crossing_point_separation
        # iz refers to the starting crossing, jz to the final crossing
        # generate starting crossing
        if random.random()>0.5:
            # start from left - right side
            ix = 0
            if random.random()>0.5:
                ix = streets_per_side - 1
            iy = random.randint(1, streets_per_side - 2)
        else:
            # start from bottom - top side
            iy = 0
            if random.random()>0.5:
                iy = streets_per_side - 1
            ix = random.randint(1, streets_per_side-2);
        # generate final crossing by simetry of initial
        jx = streets_per_side - 1 - ix; jy = streets_per_side - 1 - iy
        initial_crossing = (ix, iy)
        final_crossing = (jx, jy)
        return initial_crossing, final_crossing

    def update(self, dt):
        for car in self.cars:
            if car.state == 'free':
                initial_crossing, final_crossing = self.generate_travel()
                car.do_travel(initial_crossing, final_crossing)
            if car.state == 'traveling':
                car.update(dt)
        # handle collisions
        self.collman.clear()
        for car in self.cars:
            self.collman.add(car)
        for car, other in self.collman.iter_all_collisions():
            if car.state != 'burning':
                car.e_burn()
            if other.state != 'burning':
                other.e_burn()

description = """
Example for the collision module.
It should be seen like a top view of city streets with green circles
traveling the streets. When a circle colides with other, it should turn red.
"""

def main():
    print(description)
    director.init(width=view_width, height=view_height)
    scene = cocos.scene.Scene()
    city = City()
    scene.add(city)
    director.run(scene)

if __name__ == '__main__':
    main()
