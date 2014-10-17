from __future__ import division, print_function, unicode_literals

# collision_model tests

# aarect_circles1 test
import cocos.collision_model as cm
import cocos.euclid as eu

class Obj_with_shape(object):
    def __init__(self, name, cshape):
        self.name = name
        self.cshape = cshape

def create_obj_with_aarect(name, center, rx, ry):
    shape = cm.AARectShape(center, rx, ry)
    obj = Obj_with_shape(name, shape)
    return obj

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

# see aarect_circle1_data.png for visualization, was ploted with func
# plot_aarect_circle_data1
def aarect_circle_data1(offset):
    rx_1 = 0.75
    ry_1 = 1.00
    center = eu.Vector2(0.0, 0.0) + offset
    
    center_aarect = create_obj_with_aarect('center', center, rx_1, ry_1)

    refpoints = [ # quadrants NE, NW, SW, SE 
        (1.0, 0.0), (1.0, 0.5), (1.0, 1.0), (0.5, 1.0), 
        (0.0, 1.0), (-0.5, 1.0), (-1.0, 1.0), (-1.0, 0.5),
        (-1.0, 0.0), (-1.0, -0.5), (-1.0, -1.0), (-0.5, -1.0),
        (0.0, -1.0), (0.5, -1.0), (1.0, -1.0), (1.0, -0.5), 
        ]
    deltas = [
        (1.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0),
        (0.0, 1.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, 0.0),
        (-1.0, 0.0), (-1.0, 0.0), (-1.0, -1.0), (0.0, -1.0),
        (0.0, -1.0), (0.0, -1.0), (1.0, -1.0), (1.0, 0.0)
        ]
    
    def get_ring(ring_name, rx, ry, child_scale, distance, offset):
        # note: start parameter for enumerate() only available for python 2.6+
        ring = set()
        r = ry * child_scale
        for i in range(0, 16):
            rf_x , rf_y = refpoints[i]
            dx , dy = deltas[i]
            v = eu.Vector2(rf_x * rx, rf_y * ry)
            d = eu.Vector2(dx, dy).normalized()
            closest_point = v + distance * d
            center = closest_point + r * d 
            circle = create_obj_with_circle(
                    "%s, distance %5.3f, ray %2d"%(ring_name, distance, i),
                    center + offset, r,
                    )
            ring.add(circle)
        return ring
    
    child_scale = 0.1
    distance = -0.05
    ring_touching = get_ring("ring_touching", rx_1, ry_1, child_scale,
                             distance, offset)

    near_distance = -distance
    ring_near = get_ring("ring_near", rx_1, ry_1, child_scale,
                             near_distance, offset)
    
    far_distance = 0.17
    ring_far = get_ring("ring_far", rx_1, ry_1, child_scale,
                             far_distance, offset)

    rays = range(16)
    return (center_aarect, ring_touching, ring_near, ring_far,
            near_distance, far_distance, rays)

            
def plot_aarect_circle_data1(offset):
    (center_aarect, ring_touching, ring_near, ring_far,
     near_distance, far_distance, rays) = aarect_circle_data1(offset)

    rx = center_aarect.cshape.rx
    ry = center_aarect.cshape.ry
    small = create_obj_with_aarect('small', center_aarect.cshape.center,
                                rx - near_distance*2.0, ry - near_distance*2.0)
    

    def get_aarect_params(obj):
        x, y = obj.cshape.center
        rx = obj.cshape.rx
        ry = obj.cshape.ry
        #pylab wants lower left corner and width , height
        
        return obj.name, x-rx, y-ry, rx*2, ry*2
    
    def get_circle_params(obj):
        x, y = obj.cshape.center 
        return obj.name, x, y, obj.cshape.r
    
    import pylab
    fig = pylab.figure(figsize=(6.0, 6.0)) #size in inches
    fig.suptitle('aarect_circle_data1', fontsize=12)
    pylab.axes().set_aspect('equal') # aspect ratio

    name, x, y, w, h = get_aarect_params(center_aarect)
    rect = pylab.Rectangle((x,y), w, h,  ec='black', fc='none')
    pylab.gca().add_patch(rect)
    xmin = x
    xmax = x + w
    ymin = y
    ymax = y + h  

##    rx = center_aarect.cshape.rx
##    ry = center_aarect.cshape.ry
##    small = create_obj_with_aarect('small', center_aarect.cshape.center,
##                                rx - near_distance*2.0, ry - near_distance*2.0)
##    name, x, y, w, h = get_params(small)
##    rect = pylab.Rectangle((x,y), w, h,  ec='g', fc='none')
##    pylab.gca().add_patch(rect)


    for ring, color in [ (ring_touching, 'r'), (ring_near, 'g'),
                         (ring_far, 'b') ]:
        for obj in ring:
            name, x, y, r = get_circle_params(obj)
            cir = pylab.Circle((x,y), radius=r,  ec=color, fc='none')
            pylab.gca().add_patch(cir)
    xmin = xmin - (far_distance + r)*2.5
    xmax = xmax + (far_distance + r)*2.5
    ymin = ymin -(far_distance + r)*1.5
    ymax = ymax + (far_distance + r)*1.5
    ymin = -2.5
    # axis: xmin, xmax, ymin, ymax
    pylab.axis([xmin, xmax, ymin, ymax])

    # make legends
    labels = ['center_aarect', 'overlapping ring', 'near ring', 'far ring']
    colors = ['black', 'r', 'g', 'b' ]
    dummys = [ pylab.Line2D([0,1], [0,1], lw=2.0, c=e) for e in colors]
    pylab.gca().legend(dummys, labels, ncol=2, loc='lower center')

    #pylab.show()
    pylab.savefig('aarect_circle1_data.png')

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
             [0.0, 100.0, 0.0, 100.0, 0.5, 0.5],
             (2.0, 2.0)
             ),
        }

    for name in cases:
        metafunc.addcall(id=name, funcargs=dict(zip(param_names, cases[name])))


fe = 1.0e-4    
def test_collman_aarects(variant, ctor_args, offset):
    """
    Tests collision manager basic behavoir when shape is AARectShape,
    test data is defined by aabb_data1(offset),
    the collision manager variant is determined by 'variant',
    and 'ctor_args' provide the parameters needed to instantiate the
    collision manager.

    'variant' is the class name to use, and the class definition is assumed
    to be in the module cocos.collision_model
    """
    emptyset = set()
    (center_aarect, ring_touching, ring_near, ring_far,
     near_distance, far_distance, rays) = aarect_circle_data1(eu.Vector2(*offset))

    collman_cls = getattr(cm, variant)
    collman = collman_cls(*ctor_args)

    collman.add(center_aarect)
    for ring in [ ring_touching, ring_near, ring_far ]:
        for circle in ring:
            collman.add(circle)

    # all objs in data1 are known
    assert collman.knows(center_aarect)
    for ring in [ ring_touching, ring_near, ring_far ]:
        for circle in ring:
            collman.knows(circle)

    # the set of know objects is exactly the set of objects in data1
    assert collman.known_objs() == (set([center_aarect]) | ring_touching |
                                  ring_near | ring_far) 

    touching_result = collman.objs_colliding(center_aarect)

    # no repetitions
    touching = set(touching_result)
    assert len(touching) == len(touching_result)

    # obj is not in objs_colliding_with(obj)
    assert center_aarect not in touching

    # any in ring_touching is touching
    assert ring_touching <= touching

    # none of ring_near touches
    assert (ring_near & touching) == emptyset

    # none of ring_far touches
    assert (ring_far & touching) == emptyset

    # no extraneous values in touching
    assert ring_touching == touching

    # the generator form of touching gives same result than objs_colliding
    touching_from_generator = [e for e in collman.iter_colliding(center_aarect)]
    assert len(touching_from_generator) == len(touching)
    assert set(touching_from_generator) == touching


    # test with short near_distance, should be same as before
    short_distance = 0.9 * near_distance
    nears1_result = collman.objs_near(center_aarect, short_distance)
    #  no repetitions
    nears1 = set(nears1_result)
    assert len(nears1) == len(nears1_result)
    #  expected due to short near_distance
    assert nears1 == ring_touching

    # similar using objs_near_wdistance
    od_list = collman.objs_near_wdistance(center_aarect, short_distance)
    assert len(od_list) == len(ring_touching)
    assert set([a for a,b in od_list]) == ring_touching
    # and distances are near 0.0
    for a,d in od_list:
        assert abs(d-0.0)<fe

    # test with near distance to accept ring_near and reject ring_far
    n_distance = 0.9*near_distance + 0.1*far_distance
    nears2 = set(collman.objs_near(center_aarect, n_distance))
    assert (ring_far & nears2) == emptyset
    ##pprint_container('nears2:', nears2)
    ##pprint_container('ring_touching | ring_near', ring_touching | ring_near)
    assert nears2 == (ring_touching | ring_near)

    # similar using objs_near_wdistance
    od_list = collman.objs_near_wdistance(center_aarect, n_distance)
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
    for ray in rays:
        d[" ray %2d"%ray] = []
    
    for obj, other in collman.iter_all_collisions():
        # no collision with itself
        assert obj is not other
        # collision touching center
        if obj.name == 'center' or other.name == 'center':
            if obj.name == 'center':
                li_touching_center.append(other)
            else:
                li_touching_center.append(obj)
        else:
            # collisions not touching center
            obj_ring, obj_distance, obj_ray = obj.name.split(',')
            other_ring, other_distance, other_ray = obj.name.split(',')
            assert obj_ray == other_ray
            assert obj_ray in d
            if id(obj)>id(other):
                obj, other = other, obj
            d[obj_ray].append((obj, other))

    #      the ones touching center are correct
    assert len(li_touching_center) == len(touching)
    assert set(li_touching_center) == touching

    #      all the others
    for k in d:
        # no repetitions
        li = d[k]; si = set(li)
        assert len(li) == len(si)
        # all collisions for the ray
        assert len(si) == 2
    

    # removing center_aarect
    collman.remove_tricky(center_aarect)
    assert not collman.knows(center_aarect)
    assert center_aarect not in collman.known_objs()
    assert collman.known_objs() == (ring_touching | ring_near | ring_far)

    # any_near, with obj not known
    rx = center_aarect.cshape.rx
    ry = center_aarect.cshape.ry
    small = create_obj_with_aarect('small', center_aarect.cshape.center,
                                rx - near_distance*2.0, ry - near_distance*2.0)
    #   param 'near_distance' selected to obtain return None
    assert collman.any_near(small, near_distance/2.0) is None

    #   param 'near_distance' selected to obtain  a known object (weak)
    assert collman.any_near(small, near_distance*2.1) is not None

    # any near with known object
    collman.add(small)
    assert collman.any_near(small, near_distance/2.0) is None
    


#plot_aarect_circle_data1(eu.Vector2(0.0, 0.0))  
