
import cocos.collision_model as cm

# version 0.1, later it would be better to upgrade CShape to ShapeRect and
# use a real car image
def mRobotCar(object):
    crossing_point_separation = 1.0
    distance_between_crossings = 1.0
    burn_time = 2.0
    radius = 0.1
    def __init__(self):
        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), mRobotCar.radius)
        self.free = True
        self.burning = False
        self.update = self.update_position
        
    def do_travel(self, initial_crossing, final_crossing):
        self.next_crossing = initial_crossing
        self.final_crossing = final_crossing
        self.update_when_crossing_reached()
        self.free = False
        self.burning = False

    def update_when_crossing_reached(self):
        # set position exactly at old crossing
        ix, iy = self.next_crossing
        self.x = float(ix)
        self.y = float(iy)

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
        fastness = self.crossing_point_separation / self.time_to_next_crossing
        if self.move_in_x:
            self.scalar_vel = dx * fastness
        else:
            self.scalar_vel = dy * fastness

    def is_travel_completed(self):
        return ((self.elapsed > self.arrival) and
                (self.next_crossing == self.final_crossing))

    def update_position(self, dt):
        """
        dont call this when self.traveling == False
        """
        self.elapsed += dt
        if self.elapsed > self.arrival:
            # crossing reached
            if self.next_crossing == self.final_crossing:
                # travel finished
                self.traveling = False
            else:
                self.update_when_crossing_reached()
        else:
            # between crossings
            if self.move_in_x:
                self.x += self.scalar_vel*dt
            else:
                self.y += self.scalar_vel*dt
        # update cshape
        self.cshape.center = self.x, self.y

    def begin_burn(self):
        self.elapsed_burn_time = 0.0
        self.burning = True
        self.update = self.update_burning

    def end_burn(self):
        self.burning = False
        self.free = True
        self.update = self.update_position

    def update_burning(self, dt):
        self.elapsed_burn_time += dt
        if self.elapsed_burn_time > self.burn_time:
            self.end_burn()


class mCity(object):
    def __init__(self, streets_per_side=5, time_to_next_crossing=1.0,
                 distance_between_crossings=1.0, car_size = 0.1, collman=None):
        """
        """
        self.streets_per_side = streets_per_side
        self.pool_car_size = None
        self.time_to_next_crossing = time_to_next_crossing
        self.distance_between_crossings = distance_between_crossings
        self.car_size = car_size
        self.collman = None

        self.cars = []

    def set_actor_quantity(self, n):
        self.pool_car_size = n
        while n > len(self.cars):
            car = mRobotCar()
            self.cars.append(car)
            if isinstance(self.collman, cm.CollisionManagerBruteForce):
                self.collman.add(car)        

    def get_travel(self):
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
            if car.free:
                initial_crossing, final_crossing = self.generate_travel()
                car.do_travel(initial_crossing, final_crossing)
            car.update(dt)

        # update collman
        if not isinstance(self.collman, cm.CollisionManagerBruteForce):
            add = self.collman.add
            self.collman.clear()
            for actor in self.cars:
                add(actor)
    
        # handle collisions
        for car, other in self.collman.iter_all_collisions():
            if not car.burning:
                car.do_burn()
            if not other.burning:
                other.do_burn()
                    
                                        
print '\n *** unfinished, work in progress ***'
