from __future__ import division, print_function, unicode_literals

# collision_model tests

# circles1 test
import cocos.collision_model as cm
import cocos.euclid as eu
from math import sin, cos, radians

class Obj_with_shape(object):
    def __init__(self, name, cshape):
        self.name = name
        self.cshape = cshape

def create_obj_with_circle(name, center, r):
    shape = cm.CircleShape(center, r)
    obj = Obj_with_shape(name, shape)
    return obj

def pprint_container(heading, container):
    sl = [s.name for s in container]
    sl.sort()
    print(heading)
    for s in sl:
        print("\t%s"%s)

# see circle1_data.png for visualization, was ploted with func
# plot_circle_data1
def circle_data1(offset):
    r1 = 1.5
    center = eu.Vector2(0.0, 0.0) + offset
    
    center_circle = create_obj_with_circle('center', center, r1)

    r2 = 0.3
    d1 = (r1 + r2) - 0.1
    angles = [a for a in range(360, 1, -360//12)]
    ring_touching = set()
    for a in angles:
        center = d1 * eu.Vector2(cos(radians(a)), sin(radians(a))) + offset
        circle = create_obj_with_circle("ring_touching, distance 0.0, angle %3s"%a, center, r2)
        ring_touching.add(circle)

    near_distance = 0.1
    d2 = (r1 + r2) + near_distance
    angles = [a for a in range(360, 1, -360//12)]
    ring_near = set()
    for a in angles:
        center = d2 * eu.Vector2(cos(radians(a)), sin(radians(a))) + offset
        circle = create_obj_with_circle("ring_near, distance 0.1, angle %3s"%a,
                                        center, r2)
        ring_near.add(circle)

    far_distance = 0.2
    d3 = (r1 + r2) + far_distance
    angles = [a for a in range(360, 1, -360//12)]
    ring_far = set()
    for a in angles:
        center = d3 * eu.Vector2(cos(radians(a)), sin(radians(a))) + offset
        circle = create_obj_with_circle("ring_far, distance 0.2, angle %3s"%a,
                                        center, r2)
        ring_far.add(circle)

    return (center_circle, ring_touching, ring_near, ring_far,
            near_distance, far_distance, angles)

            
def plot_circle_data1(offset):
    (center_circle, ring_touching, ring_near, ring_far,
     near_distance, far_distance, angles) = circle_data1(offset)

    def get_params(obj):
        x, y = obj.cshape.center 
        return obj.name, x, y, obj.cshape.r
    
    import pylab
    fig = pylab.figure(figsize=(6.0, 6.0)) #size in inches
    fig.suptitle('circle_data1', fontsize=12)
    pylab.axes().set_aspect('equal') # aspect ratio

    name, x, y, r = get_params(center_circle)
    cir = pylab.Circle((x,y), radius=r,  ec='black', fc='none')
    pylab.gca().add_patch(cir)
    xmax = r

    for ring, color in [ (ring_touching, 'r'), (ring_near, 'g'),
                         (ring_far, 'b') ]:
        for obj in ring:
            name, x, y, r = get_params(obj)
            cir = pylab.Circle((x,y), radius=r,  ec=color, fc='none')
            pylab.gca().add_patch(cir)
    ymin = -(xmax + (2*r + far_distance)*3)
    xmax = xmax + (2*r + far_distance)*2

    # axis: xmin, xmax, ymin, ymax
    pylab.axis([-xmax, xmax, ymin, xmax])

    # make legends
    labels = ['center_circle', 'overlapping ring', 'near ring', 'far ring']
    colors = ['black', 'r', 'g', 'b' ]
    dummys = [ pylab.Line2D([0,1], [0,1], lw=2.0, c=e) for e in colors]
    pylab.gca().legend(dummys, labels, ncol=2, loc='lower center')

    #pylab.show()
    pylab.savefig('circle1_data.png')

def pytest_generate_tests(metafunc):
    param_names = ['variant', 'ctor_args', 'offset']
    cases = {
        "BruteForce":
            ('CollisionManagerBruteForce', [], (2.2, 3.7)),
        "Grid, target don't crosses bucket edges":
            ('CollisionManagerGrid',
             [0.0, 100.0, 0.0, 100.0, 4.0, 4.0],
             (2.0, 2.0)
             ),
        "Grid, target crosses horizontal bucket edge":
            ('CollisionManagerGrid',
             [0.0, 100.0, 0.0, 100.0, 4.0, 4.0],
             (2.0, 4.0)
             ),
        "Grid, target crosses vertical bucket edge":
            ('CollisionManagerGrid',
             [0.0, 100.0, 0.0, 100.0, 4.0, 4.0],
             (4.0, 2.0)
             ),
        "Grid, target crosses vertical and horizontal bucket edges":
            ('CollisionManagerGrid',
             [0.0, 100.0, 0.0, 100.0, 4.0, 4.0],
             (4.0, 4.0)
             ),
        "Grid, target bigger than cell":
            ('CollisionManagerGrid',
             [0.0, 100.0, 0.0, 100.0, 2.0, 2.0],
             (2.0, 2.0)
             ),
        }

    for name in cases:
        metafunc.addcall(id=name, funcargs=dict(zip(param_names, cases[name])))


fe = 1.0e-4    
def test_collman_circles(variant, ctor_args, offset):
    """
    Tests collision manager basic behavoir when shape is circle,
    test data is defined by circle_data1(offset),
    the collision manager variant is determined by 'variant',
    and 'ctor_args' provide the parameters needed to instantiate the
    collision manager.

    'variant' is the class name to use, and the class definition is assumed
    to be in the module cocos.collision_model
    """
    emptyset = set()
    (center_circle, ring_touching, ring_near, ring_far,
     near_distance, far_distance, angles) = circle_data1(eu.Vector2(*offset))

    collman_cls = getattr(cm, variant)
    collman = collman_cls(*ctor_args)

    collman.add(center_circle)
    for ring in [ ring_touching, ring_near, ring_far ]:
        for circle in ring:
            collman.add(circle)

    # all objs in data1 are known
    assert collman.knows(center_circle)
    for ring in [ ring_touching, ring_near, ring_far ]:
        for circle in ring:
            collman.knows(circle)

    # the set of know objects is exactly the set of objects in data1
    assert collman.known_objs() == (set([center_circle]) | ring_touching |
                                  ring_near | ring_far) 

    touching_result = collman.objs_colliding(center_circle)

    # no repetitions
    touching = set(touching_result)
    assert len(touching) == len(touching_result)

    # obj is not in objs_colliding_with(obj)
    assert center_circle not in touching

    # any in ring_touching is touching
    assert ring_touching <= touching

    # none of ring_near touches
    assert (ring_near & touching) == emptyset

    # none of ring_far touches
    assert (ring_far & touching) == emptyset

    # no extraneous values in touching
    assert ring_touching == touching

    # the generator form of touching gives same result than objs_colliding
    touching_from_generator = [e for e in collman.iter_colliding(center_circle)]
    assert len(touching_from_generator) == len(touching)
    assert set(touching_from_generator) == touching


    # test with short near_distance, should be same as before
    short_distance = 0.9 * near_distance
    nears1_result = collman.objs_near(center_circle, short_distance)
    #  no repetitions
    nears1 = set(nears1_result)
    assert len(nears1) == len(nears1_result)
    #  expected due to short near_distance
    assert nears1 == ring_touching

    # similar using objs_near_wdistance
    od_list = collman.objs_near_wdistance(center_circle, short_distance)
    assert len(od_list) == len(ring_touching)
    assert set([a for a,b in od_list]) == ring_touching
    # and distances are near 0.0
    for a,d in od_list:
        assert abs(d-0.0)<fe

    # test with near distance to accept ring_near and reject ring_far
    n_distance = 0.9*near_distance + 0.1*far_distance
    nears2 = set(collman.objs_near(center_circle, n_distance))
    assert (ring_far & nears2) == emptyset
    pprint_container('nears2:', nears2)
    pprint_container('ring_near', ring_near)        
    assert nears2 == (ring_touching | ring_near)

    # similar using objs_near_wdistance
    od_list = collman.objs_near_wdistance(center_circle, n_distance)
    nears2 = set(od_list)
    assert len(od_list) == len(nears2)
    assert set([a for a,b in od_list]) == (ring_touching | ring_near)
    # and distances match
    for a,d in od_list:
        assert ((a in ring_touching and abs(d) < fe) or
                (a in ring_near and abs(d-near_distance)<fe))

    # all_collisions
    li_touching_center = []
    d = {}
    for a in angles:
        d[" angle %3s"%a] = []
    
    for obj, other in collman.iter_all_collisions():
        # no collision with itself
        assert obj is not other
        if obj.name == 'center' or other.name == 'center':
            if obj.name == 'center':
                li_touching_center.append(other)
            else:
                li_touching_center.append(obj)
        else:
            obj_ring, obj_distance, obj_angle = obj.name.split(',')
            other_ring, other_distance, other_angle = obj.name.split(',')
            assert obj_angle == other_angle
            assert obj_angle in d
            if id(obj)>id(other):
                obj, other = other, obj
            d[obj_angle].append((obj, other))

    #      the ones touching center are correct
    assert len(li_touching_center) == len(touching)
    assert set(li_touching_center) == touching

    #      all the others
    for k in d:
        # no repetitions
        li = d[k]; si = set(li)
        assert len(li) == len(si)
        # all collisions for the angle
        assert len(si) == 3

    # removing center_circle
    collman.remove_tricky(center_circle)
    assert not collman.knows(center_circle)
    assert center_circle not in collman.known_objs()
    assert collman.known_objs() == (ring_touching | ring_near | ring_far)

    # any_near, with obj not known
    r = center_circle.cshape.r
    small = create_obj_with_circle('small', center_circle.cshape.center,
                                    r - near_distance*2.0)
    #   param 'near_distance' selected to obtain return None
    assert collman.any_near(small, near_distance/2.0) is None

    #   param 'near_distance' selected to obtain  a known object (weak)
    assert collman.any_near(small, near_distance*2.1) is not None

    # any near with known object
    collman.add(small)
    assert collman.any_near(small, near_distance/2.0) is None
    
            

#plot_circle_data1(eu.Vector2(0.0, 0.0))  
