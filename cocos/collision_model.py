import operator as op
import math
import cocos.euclid as eu

###### interfaces, abstract base clases ######################################

# cshape reference interfase 
class Cshape(object):
    def overlaps(self, other):
        """
        Returns a boolean, True if itself overlaps other
        """
        pass

    def distance(self, other):
        """
        Returns a float, distance from itself to other;
        not necesarily euclidean distance
        """
        pass

    def near_than(self, other, near_distance):
        """
        Returns a boolean, True if distance(self, other)<=near_distance
        """
        pass

    def touchs_point(self, x, y):
        """
        Returns a boolean, True if the point (x,y) overlaps the shape
        """
        pass

    def fits_in_box(self, packed_box):
        """
        Returns a boolean, True if the shape fully fits into the axis aligned
        box defined by packed_box (== minx, maxx, miny, maxy)
        """
        pass

    def minmax(self):
        """
        Returns a four float tuple  xmin, xmax, ymin, ymax definning the
        axis aligned bounding box for itself
        
        That's equivalent to
        x,y hits the shape implies (xmin <= x <= xmax and ymin <= y <= ymax)

        Useful for a generic 'which buckets overlaps itself'
        """
        pass


##    def collision_details(self, other):
##        """
##        returns collision_point, collision_normal, overlap_mesure 
##        """
##        pass

# collidable reference
# an object obj is collidable if and only if:
#   . it has a member called 'cshape'
#   . obj.cshape supports the interfase Cshape


# collision manager interfase
class CollisionManager(object):
    """
    Role: answer questions about proximity or collision with known objects

    Objects must comply with:
        . obj has a member called cshape
        . obj.cshape supports the interface Cshape
        . as a limitation imposed by the current Cshapes implementations, a
        unique concrete Cshape is allowed across all objects know by a
        CollisionManager instance.
        By example, all objects should have a CircleShape cshape, or all
        objects should have a AARectShape cshape.

    CollisionManager don't automatically tracks changes in obj.cshape, it is
    user code responsability to update the collision manager instance when
    obj.cshape values changes. (By example, if obj position changes) 
    Eficient ways of doing this are:

    General use case:

    The game level will have a CollisionManager instance, lets call it collman.
    Then at each frame you do:
        . call collman.clear  (it will empty collision manager)
        . call collman.add for all collidable actors still alive
        . do the game logic, asking all the questions you want about collision;
        . as part of the frame update, each object should end with an updated
        cshape.

    Special case optimization:
    
    If lot of the objects are static and only a *few* dynamic ones needs to
    interact with the statics, the best is to have two collision managers:
    one for the static objects, the other for all dynamics objects.
    Then, when starting a level:
        add the static collidables to collman_static
    In each frame:
        . call collman_dynamic.clear
        . add to collman_dynamic all the dynamic collidables
        . do the game logic, use remove_tricky to remove in collman_static
        . as part of the frame update, each dynamic should end with an updated
        cshape.

    An example of this situation is an arcade game with lots of enemies and
    lots of goodies (food, coins, powerups) where the goodies are static and
    only interacts with player.
    goodies-player interaction will use collman_goodies.objs_colliding(player),
    player-enemies interactions will use collman_dynamic.

    Note that the few dynamics that interacts with statics are not added to
    collman_static.
    Also, there can be lots of dynamics, whenever only a few interacts with the
    statics.

    """
    def add(self, obj):
        """
        Makes obj a know entity
        """
        pass

    def remove_tricky(self, obj):
        """*(obj should have the same .cshape value that when added)*
        Makes CollisionManager forget about obj, thus no further query will
        return obj.

        Should only be used in a collman that most of the frames don't changes.
        """

    def clear(self):
        """
        Empties the known set
        """
        pass

    def they_collide(self, obj1, obj2):
        """
        Returns a boolean, True if obj1 overlaps objs2

        obj1, obj2 are not required to be known objects 
        """
        pass

    def objs_colliding(self, obj):
        """
        Returns a container with known objects that overlaps obj,
        excluding obj itself

        obj is not required to be a known object
        """
        pass

    def iter_colliding(self, obj):
        """
        A lazy iterator over objects colliding with obj, allows to spare some
        CPU when the loop procesing the colissions breaks before exausting
        the collisions.

        Usage:
        for other in collision_manager.iter_colliding(obj):
            # process event 'obj touches other'

        obj is not required to be a known object
        """
        pass

    def any_near(self, obj, near_distance):
        """
        Returns None if no know object (except itself) is near than
        near_distance, else an arbitrary known object with distance
        less than near_distance

        obj is not required to be a known object
        """
        pass

    def objs_near(self, obj, near_distance):
        """
        Returns a container the objects known by collision manager that are at
        distance to obj less or equal than near_distance, excluding itself.
        Notice that it includes the ones colliding with obj.
        obj is not required to be a known object
        """
        pass


    def objs_near_wdistance(self, obj, near_distance):
        """
        Returns a list of the (other, distance) pairs that mentions all the
        registered objects at distance less or equal than near_distance to obj,
        except obj itself.
        Notice that it includes the ones colliding with obj.
        obj is not required to be a known object
        If the game logic wants the list ordered by ascending distances, use
        ranked_objs_near instead.        
        """
        pass

    def ranked_objs_near(self, obj, near_distance):
        """
        Same as objs_near_wdistance but the list is ordered in increasing distance
        obj is not required to be a known object
        """
        pass

    def iter_all_collisions(self):
        """
        Iterator that exposes all collisions between known objects.
        At each step it will yield a pair (obj, other).
        If (obj1, obj2) is seen when consuming the iterator, then (obj2, obj1)
        will not be seen.
        In other worlds, 'obj1 collides with obj2' means (obj1, obj2) or
        (obj2, obj1) will appear in the iterator output but not both.
        """

    def knows(self, obj):
        """-> True if obj was added to the collision manager
        Used for debug and testing.
        """
        pass

    def known_objs(self):
        """-> set of objects known by the CollisionManager
        Used for debug and testing.
        """
        pass

    def objs_touching_point(self, x, y):
        """ -> container with known objects touching point (x, y)

        Useful for mouse pick
        """
        pass

    def objs_into_box(self, minx, maxx, miny, maxy):
        """-> container with know objects that fully fits into the aabb defined by params

        Useful for elastic box selection
        """


###### Cshape implementations #################################################


class CircleShape(object):
    def __init__(self, center, r):
        self.center = center
        self.r = r

    def overlaps(self, other):
        return abs(self.center - other.center) < self.r + other.r

    def distance(self, other):
        d = abs(self.center - other.center) - self.r - other.r
        if d<0.0:
            d = 0.0
        return d
    
    def near_than(self, other, near_distance):
        return abs(self.center - other.center) <= self.r + other.r + near_distance

    def touchs_point(self, x, y):
        return (self.center - (x,y)).magnitude() <= self.r

    def fits_in_box(self, packed_box):
        r = self.r
        return ( ((packed_box[0] + r) <= self.center[0] <= (packed_box[1] - r)) and
                 ((packed_box[2] + r) <= self.center[1] <= (packed_box[3] - r)) )

    def minmax(self):
        r = self.r
        return (self.center[0]-r, self.center[0]+r,
                self.center[1]-r, self.center[1]+r)
        
##    def collision_details(self, other):
##        r1 = self.r
##        r2 = other.r
##        R = r1 + r2
##        d = abs(self.center - other.center)
##
##        # midle point in the segment over the line passing by both centers,
##        # with extremes in the intersection with each circle 
##        contact_point =  ...
##
##        # normal to self.center-other.center; prefered sign (?)
##        # also it can be normal to contact_point - self.center
##        contact_normal = ...
##
##        # R-d is an absolute mesure; (R-d)/R would be a relative mesure
##        # typical use related to elastic force / overlapping avoidance
##        overlapping_measure = ...
##
##        # They will be harder to define and costly to calculate for
##        # CshapeRect
##
##        return contact_point, contact_normal, overlapping_measure 


class AARectShape(object):
    """
    Rectangles with sides paralell to the coordinate axis.
    Good if actors don't rotate.
    """
    def __init__(self, center, half_width, half_height):
        self.center = center
        self.rx = half_width
        self.ry = half_height
        
    def overlaps(self, other):
        return ( abs(self.center[0] - other.center[0]) < self.rx + other.rx and
                 abs(self.center[1] - other.center[1]) < self.ry + other.ry )

    def distance(self, other):
        d = max((abs(self.center[0] - other.center[0])-self.rx - other.rx,
                abs(self.center[1] - other.center[1])-self.ry - other.ry ))
        if d<0.0:
            d = 0.0
        return d
    
    def near_than(self, other, near_distance):
        return ( abs(self.center[0] - other.center[0]) - self.rx - other.rx < near_distance and
                 abs(self.center[1] - other.center[1]) - self.ry - other.ry < near_distance)

    def touchs_point(self, x, y):
        return ( abs(self.center[0] - x) < self.rx and
                 abs(self.center[1] - y) < self.ry )

    def fits_in_box(self, packed_box):
        return ( (packed_box[0] + self.rx <= self.center[0] <= packed_box[1] - self.rx) and
                 (packed_box[2] + self.ry <= self.center[1] <= packed_box[3] - self.ry) )

    def minmax(self):
        return (self.center[0] - self.rx, self.center[0] + self.rx,
                self.center[1] - self.ry, self.center[1] + self.ry)


###### CollisionManager implementations #######################################


class CollisionManagerBruteForce(object):
    def __init__(self):
        self.objs = set()

    def add(self, obj):
        #? use weakref ? python 2.7 has weakset
        self.objs.add(obj)

    def remove_tricky(self, obj):
        self.objs.remove(obj)

    def clear(self):
        self.objs.clear()

    def they_collide(self, obj1, obj2):
        return obj1.cshape.overlaps(obj2.cshape)

    def objs_colliding(self, obj):
        f_overlaps = obj.cshape.overlaps
        return [other for other in self.objs if
                (other is not obj) and f_overlaps(other.cshape)]

    def iter_colliding(self, obj):
        f_overlaps = obj.cshape.overlaps
        for other in self.objs:
            if other is not obj and f_overlaps(other.cshape):
                yield other

    def any_near(self, obj, near_distance):
        f_near_than = obj.cshape.near_than
        for other in self.objs:
            if other is not obj and f_near_than(other.cshape,near_distance):
                return other
        return None
        
    def objs_near(self, obj, near_distance):
        f_near_than = obj.cshape.near_than
        return [other for other in self.objs if
                (other is not obj) and f_near_than(other.cshape,near_distance)]

    def objs_near_wdistance(self, obj, near_distance):
        f_distance = obj.cshape.distance
        res = []
        for other in self.objs:
            if other is obj:
                continue
            d = f_distance(other.cshape)
            if d<= near_distance:
                res.append((other, d))
        return res

##    def objs_near_wdistance(self, obj, near_distance):
##        # alternative version, needs python 2.5+
##        f_distance = obj.cshape.distance
##        def f(other):
##            return other, f_distance(other.cshape)
##        import itertools as it
##        return [(other, d) for other,d in it.imap(f, self.objs) if
##                                                        (other is not obj) and
##                                                        (d <= near_distance)]
    def ranked_objs_near(self, obj, near_distance):
        tmp = objs_near_wdistance(obj, near_distance)
        tmp.sort(key=op.itemgetter(1))
        return tmp

    def iter_all_collisions(self):
        # O(n**2)
        for i, obj in enumerate(self.objs):
            f_overlaps = obj.cshape.overlaps
            for j, other in enumerate(self.objs):
                if j>=i:
                    break
                if f_overlaps(other.cshape):
                    yield (obj, other)
                
    def knows(self, obj):
        """-> True if obj was added to the collision manager
        Used for debug and testing.
        """
        return obj in self.objs

    def known_objs(self):
        """-> set of objects known by the CollisionManager
        Used for debug and testing.
        """
        return self.objs

    def objs_touching_point(self, x, y):
        touching = set()
        for obj in self.objs:
            if obj.cshape.touchs_point(x, y):
                touching.add(obj)
        return touching

    def objs_into_box(self, minx, maxx, miny, maxy):
        into = set()
        packed_box = minx, maxx, miny, maxy
        for obj in self.objs:
            if obj.cshape.fits_in_box(packed_box):
                into.add(obj)
        return into


class CollisionManagerGrid(object):
    def __init__(self, xmin, xmax, ymin, ymax, cell_width, cell_height):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.cell_width = cell_width
        self.cell_height = cell_height

        cols = int(math.ceil((xmax - xmin)/float(cell_width)))
        rows = int(math.ceil((ymax - ymin)/float(cell_height)))
        self.cols = cols
        self.rows = rows
        numbuckets = cols*rows
        # buckets maps cell identifier -> objs that potentially overlaps the cell
        self.buckets = [set() for k in xrange(numbuckets)]

    def add(self, obj):
        # add to any bucket it overlaps
        # for the collision logic algorithm is fine if a number of buckets
        # that don't overlap are included; this allows to use a faster
        # 'buckets_for_objects' at the cost of potentially some extra buckets
        for cell_idx in self._iter_cells_for_aabb(obj.cshape.minmax()):
            self.buckets[cell_idx].add(obj)

    def remove_tricky(self, obj):
        for cell_idx in self._iter_cells_for_aabb(obj.cshape.minmax()):
            self.buckets[cell_idx].remove(obj)

    def clear(self):
        for bucket in self.buckets:
            bucket.clear()

    def they_collide(self, obj1, obj2):
        return obj1.cshape.overlaps(obj2.cshape)

    def objs_colliding(self, obj):
        aabb = obj.cshape.minmax()
        f_overlaps = obj.cshape.overlaps
        collides = set()
        collides.add(obj)
        # do brute force with others in all the buckets obj overlaps
        for cell_id in self._iter_cells_for_aabb(aabb):
            for other in self.buckets[cell_id]:
                if other not in collides and f_overlaps(other.cshape):
                    collides.add(other)
        collides.remove(obj)
        return collides
        
    def iter_colliding(self, obj):
        aabb = obj.cshape.minmax()
        f_overlaps = obj.cshape.overlaps
        collides = set()
        collides.add(obj)
        # do brute force with others in all the buckets obj overlaps
        for cell_id in self._iter_cells_for_aabb(aabb):
            for other in self.buckets[cell_id]:
                if (other not in collides) and f_overlaps(other.cshape):
                    collides.add(other)
                    yield other

    def any_near(self, obj, near_distance):
        minx, maxx, miny, maxy = obj.cshape.minmax()
        minx -= near_distance
        maxx += near_distance
        miny -= near_distance
        maxy += near_distance
        f_distance = obj.cshape.distance
        # do brute force with others in all the buckets inflated shape overlaps
        for cell_id in self._iter_cells_for_aabb((minx, maxx, miny, maxy)):
            for other in self.buckets[cell_id]:
                if other is not obj and f_distance(other.cshape) < near_distance:
                    return other
        return None

    def objs_near(self, obj, near_distance):
        minx, maxx, miny, maxy = obj.cshape.minmax()
        minx -= near_distance
        maxx += near_distance
        miny -= near_distance
        maxy += near_distance
        f_distance = obj.cshape.distance
        collides = set()
        # do brute force with others in all the buckets inflated shape overlaps
        for cell_id in self._iter_cells_for_aabb((minx, maxx, miny, maxy)):
            for other in self.buckets[cell_id]:
                if (other not in collides and
                    (f_distance(other.cshape) < near_distance)):
                    collides.add(other)
        collides.remove(obj)
        return collides

    def objs_near_wdistance(self, obj, near_distance):
        minx, maxx, miny, maxy = obj.cshape.minmax()
        minx -= near_distance
        maxx += near_distance
        miny -= near_distance
        maxy += near_distance
        f_distance = obj.cshape.distance
        collides = {}
        collides[obj] = 0.0
        # do brute force with others in all the buckets inflated shape overlaps
        for cell_id in self._iter_cells_for_aabb((minx, maxx, miny, maxy)):
            for other in self.buckets[cell_id]:
                if other not in collides:
                    d = f_distance(other.cshape)
                    if d <= near_distance:
                        collides[other] = d
                        #yield (other, d)
        del collides[obj]
        return [ (other, collides[other]) for other in collides ]
    
    def ranked_objs_near(self, obj, near_distance):
        tmp = self.objs_near_wdistance(obj, near_distance)
        tmp.sort(key=op.itemgetter(1))
        return tmp

    def iter_all_collisions(self):
        # implemented using the fact: 'a collides b' iff (there is a bucket B
        # with a in B, b in B and 'a collides b')
        known_collisions = set()
        for bucket in self.buckets:
            for i, obj in enumerate(bucket):
                f_overlaps = obj.cshape.overlaps
                for j, other in enumerate(bucket):
                    if j>=i:
                        break
                    if f_overlaps(other.cshape):
                        if id(obj)<id(other):
                            coll_id = (id(obj), id(other))
                        else:
                            coll_id = (id(other), id(obj))
                        if not coll_id in known_collisions:
                            known_collisions.add(coll_id)
                            yield (obj, other)

    def knows(self, obj):
        for bucket in self.buckets:
            if obj in bucket:
                return True
        return False

    def known_objs(self):
        objs = set()
        for bucket in self.buckets:
            objs |= bucket
        return objs

    def objs_touching_point(self, x, y):
        touching = set()
        for cell_id in self._iter_cells_for_aabb((x, x, y, y)):
            for obj in self.buckets[cell_id]:
                if obj.cshape.touchs_point(x, y):
                    touching.add(obj)
        return touching

    def objs_into_box(self, minx, maxx, miny, maxy):
        into = set()
        buckets = self.buckets
        packed_box = (minx, maxx, miny, maxy)
        for cell_idx in self._iter_cells_for_aabb(packed_box):
            for obj in buckets[cell_idx]:
                if (obj not in into) and (obj.cshape.fits_in_box(packed_box)):
                    into.add(obj)
        return into

    def _iter_cells_for_aabb(self, aabb):
        # iterate all buckets overlapping the rectangle minmax
        minx, maxx, miny, maxy = aabb
        ix_lo = int(math.floor((minx - self.xmin)/self.cell_width))
        ix_sup = int(math.ceil((maxx - self.xmin)/self.cell_width))
        iy_lo = int(math.floor((miny - self.ymin)/self.cell_height))
        iy_sup = int(math.ceil((maxy - self.ymin)/self.cell_height))

        # but disregard cells ouside world, can come from near questions
        if ix_lo < 0:
            ix_lo = 0
        if ix_sup > self.cols:
            ix_sup = self.cols
        if iy_lo < 0:
            iy_lo = 0
        if iy_sup > self.rows:
            iy_sup = self.rows

        for iy in xrange(iy_lo, iy_sup):
            contrib_y = iy * self.cols
            for ix in xrange(ix_lo, ix_sup):
                cell_id = ix + contrib_y
                yield cell_id
