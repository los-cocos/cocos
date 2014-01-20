from __future__ import division, print_function, unicode_literals

# tests implementation details

import cocos.collision_model as cm
import cocos.euclid as eu

fe = 1.0e-4

class Obj_with_shape(object):
    def __init__(self, name, cshape):
        self.name = name
        self.cshape = cshape

def create_obj_with_circle(name, center, r):
    shape = cm.CircleShape(center, r)
    obj = Obj_with_shape(name, shape)
    return obj

def test_ops_near_boundaries():
    # applies only to CollisionManagerGrid, boundaries are the grid boundaries
    w_width = 200.0
    w_height = 100.0
    cell_side = 20.00
    collman = cm.CollisionManagerGrid(0.0, w_width, 0.0, w_height, cell_side,
                                      cell_side)

    # adding object near boundaries should not fail
    radius = 5.0
    
    lo_lo = create_obj_with_circle('lo-lo',
                        eu.Vector2(radius+fe, radius+fe), radius)

    collman.add(lo_lo) #must not fail
    assert collman.knows(lo_lo)

    lo_hi = create_obj_with_circle('lo-hi',
                        eu.Vector2(radius+fe, w_height - (radius+fe)), radius)
    collman.add(lo_hi) #must not fail
    assert collman.knows(lo_hi)
    
    hi_lo = create_obj_with_circle('hi-lo',
                        eu.Vector2(w_width - (radius+fe), radius+fe), radius)
    collman.add(hi_lo) #must not fail
    assert collman.knows(hi_lo)
    
    hi_hi = create_obj_with_circle('hi-hi',
                        eu.Vector2(w_width - (radius+fe), w_height - (radius+fe)),
                        radius)
    collman.add(hi_hi) #must not fail
    assert collman.knows(hi_hi)


    # asking for others near obj should not fail if the near capsule goes out
    # of world boundaries
    
    near_distance = w_width
    nears = collman.objs_near(lo_lo, near_distance) #must not fail
    li = collman.objs_near_wdistance(lo_lo, near_distance) #must not fail
    ranked = collman.ranked_objs_near(lo_lo, near_distance) #must not fail
    
    nears = collman.objs_near(lo_hi, near_distance) #must not fail
    li = collman.objs_near_wdistance(lo_hi, near_distance) #must not fail
    ranked = collman.ranked_objs_near(lo_hi, near_distance) #must not fail
    
    nears = collman.objs_near(hi_lo, near_distance) #must not fail
    li = collman.objs_near_wdistance(hi_lo, near_distance) #must not fail
    ranked = collman.ranked_objs_near(hi_lo, near_distance) #must not fail

    nears = collman.objs_near(hi_hi, near_distance) #must not fail
    li = collman.objs_near_wdistance(hi_hi, near_distance) #must not fail
    ranked = collman.ranked_objs_near(hi_hi, near_distance) #must not fail

    nears = collman.objs_near(lo_lo, w_width + w_height)
    assert set(nears) == set([lo_hi, hi_lo, hi_hi])
