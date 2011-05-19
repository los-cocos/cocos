
import random
import time
import gc

import cocos.collision_model as cm
import c0_bouncing_balls_Model as m

base_demo_world_params = {
    'seed': 123456,
    'world_width': 800.0,
    'world_height': 600.0,
    'border_thickness': 50.0, 
    'ball_radius': 16.0,
    'fastness': 64.0,
    'k_border': 10.0,
    'k_ball': 10.0
    }

interesting_ball_quantities = [50, 100, 250, 500]

stats_fixed_params = {
    'num_frames': 100,
    'dt': 1.0 / 60.0
}

def benchmark_time_per_frame():
    benchmark = {
        'description':
            """
            Time per frame for diferent CollisionManagers, mesured over
            a number of ball quantities.
            The test situation proposes a rectangular world with elastic
            boundaries, and a number of balls that should do elastic
            collisions (not physically accurate).
            The initial condition is uniform distribution of balls in the
            rectangle, and velocity with uniform angle distribution and fixed
            modulus.
            The time per frame is estimated as
            (time needed to calculate num_frames) / num_frames

            The fixed params across all runs are
                seed: seed for random, to have same initial conditions
                world_width
                world_height
                ball_radius
                fastness: velocity modulus at start, also used in fake physics
                k_border: elastic constant for ball-borders interaction
                k_ball: elastic constant for ball-ball interactions

                num_frames: number of physic frames to calculate
                dt: time step between frames
            """,
        'name': 'bouncing balls time_per_frame',
        'fixed_params': {
            'world': base_demo_world_params,
            'stats_aquisition': stats_fixed_params,
            }
        }
        
                
    stats = {}    

    case_name = 'BruteForce'
    times = []
    for quantity in interesting_ball_quantities:
        world_params = dict(base_demo_world_params)
        random.seed(world_params.pop('seed'))
        world_params['collision_manager'] = cm.CollisionManagerBruteForce()
        world = m.World(**world_params)
        world.set_actor_quantity(quantity)
        times.append(time_per_frame(stats_fixed_params, world))
    stats[case_name] = times

    for cell_width_to_obj_width_ratio in [1.25, 1.5, 2.0, 3.0]:
        d = dict(base_demo_world_params)
        case_name = 'Grid, cell width to ball width ratio %4.2f'%cell_width_to_obj_width_ratio
        cell_side = 2.0 * d['ball_radius'] * cell_width_to_obj_width_ratio
        collman_args = (0.0, d['world_width'],
                        0.0, d['world_height'],
                        cell_side, cell_side)
        times = []
        for quantity in interesting_ball_quantities:
            world_params = dict(base_demo_world_params)
            random.seed(world_params.pop('seed'))
            world_params['collision_manager'] = cm.CollisionManagerGrid(*collman_args)
            world = m.World(**world_params)
            world.set_actor_quantity(quantity)
            times.append(time_per_frame(stats_fixed_params, world))
        stats[case_name] = times

    pprint_stats(stats)
    return stats    
        
def time_per_frame(stats_fixed_params, world):
    dt = stats_fixed_params['dt']
    num_frames = stats_fixed_params['num_frames']
    gc.collect()                 
    start_time = time.time()
    for i in xrange(num_frames):
        world.update(dt)
    gc.collect()
    end_time = time.time()
    return (end_time - start_time) / num_frames

def pprint_stats(stats):
    print "\nstats = {"
    for case in stats:
        res = stats[case]
        print "    %s:"%repr(case)
        print "        [%s, %s, %s,"%(repr(res[0]), repr(res[1]), repr(res[2])) 
        print "        %s],"%repr(res[3])
    print "    }"

def plot_benchmark_time_per_frame(ball_quantities, benchmark_results):
    import pylab
    fig = pylab.figure(figsize=(6.0, 11.0)) #size in inches
    fig.suptitle('bouncing balls time per model frame', fontsize=12)

    # thickening axes
    pylab.axis([0.0, 500, -50 , 150])
    pylab.rc('axes', linewidth=3)

    # axis labels
    pylab.xlabel(r"num balls", fontsize = 12, fontweight='bold')
    pylab.ylabel(r"time per frame in ms", fontsize = 12, fontweight='bold')

    # plot cases
    x = ball_quantities
    case_names = [ k for k in benchmark_results]
    case_names.sort()
    colors = [ 'b', 'r', 'g', 'm', '#95B9C7', '#EAC117', '#827839' ]
    for case, color in zip(case_names, colors):
        # convert time to ms
        res = [ v*1000 for v in benchmark_results[case]] 
        pylab.plot(x, res, color=color, label=case)

    # show the plots labels
    pylab.legend(loc='lower center')

    #pylab.show() # show the figure in a new window
    pylab.savefig('bouncing_balls_time_per_frame.png')

print '\nworking...'
stats = benchmark_time_per_frame()            
plot_benchmark_time_per_frame(interesting_ball_quantities, stats)
print '\n*** Done ***

## sample output: testbed windows xp sp3 32 bits, python 2.6.5, AMD athlon dual
## core 5200+, memory DDR2 800 single channel
## parameters were:
##base_demo_world_params = {
##    'seed': 123456,
##    'world_width': 800.0,
##    'world_height': 600.0,
##    'border_thickness': 50.0, 
##    'ball_radius': 16.0,
##    'fastness': 64.0,
##    'k_border': 10.0,
##    'k_ball': 10.0
##    }
##
##interesting_ball_quantities = [50, 100, 250, 500]
##
##stats_fixed_params = {
##    'num_frames': 100,
##    'dt': 1.0 / 60.0
##}
##results:      
##stats = {
##    'Grid, cell width to ball width ratio 2.00':
##        [0.0028100013732910156, 0.005940001010894775, 0.021719999313354492,
##        0.067340002059936524],
##    'Grid, cell width to ball width ratio 1.50':
##        [0.0029700016975402832, 0.0059299993515014651, 0.020939998626708985,
##        0.063599998950958248],
##    'BruteForce':
##        [0.0079700016975402833, 0.028910000324249268, 0.17374999999999999,
##        0.68999999999999995],
##    'Grid, cell width to ball width ratio 1.25':
##        [0.0029699993133544922, 0.0060899996757507327, 0.020469999313354491,
##        0.062030000686645506],
##    'Grid, cell width to ball width ratio 3.00':
##        [0.0028100013732910156, 0.0062500000000000003, 0.024220001697540284,
##        0.078750000000000001],
##    }

#pprint_stats(stats)
