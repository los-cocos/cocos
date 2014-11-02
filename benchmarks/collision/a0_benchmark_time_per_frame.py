from __future__ import division, print_function, unicode_literals

import random
import time
import gc


import a0_bouncing_balls_Model as m
# the cocos.collision_model implementation to test is imported elsewhere and
# stored in __builtins__.collision_module

# --> params that must be constants across runs for consistent results
base_demo_world_params = {
    'seed': 123456,
    'world_width': 800.0,
    'world_height': 600.0,
    'border_thickness': 50.0, 
    'ball_radius': 16.0,
    'fastness': 64.0,
    'k_border': 10.0,
    'k_ball': 10.0,

    # these are set in each case
    'cshape_cls_names': None, # must be filled 'CircleShape' #'AARectShape'
    'collision_manager': None # must be filled, see below
    }

stats_params = {
    'ball_quantities': [50, 100, 250, 500],
    'num_frames': 100,
    'dt': 1.0 / 60.0
}
# <--

# --> specify comparison variants
# each variant is a dict specifying the cases to compare

# how to specify cases
##cases = {
##    '<name case>': {
##        'collman_cls_name':'hjhjg',
##        'cshape_cls_names': ['dsdas'],
##        'collman_gen_args': [...]
##        }
##    ...
##    }

# Shape is always CircleShape, comparing performance of Collision Managers
# BruteForce vs Grid. Also, influence of cell size, relative to actors size
collman_cases = { 
    'BruteForce': {
        'collman_cls_name': 'CollisionManagerBruteForce',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': []
        },
    'Grid, cell width to ball width ratio 1.25': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [1.25] # desired (cell width) / (obj width) ratio
        },
    'Grid, cell width to ball width ratio 1.50': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [1.50]
        },
    'Grid, cell width to ball width ratio 2.00': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [2.0]
        },
    'Grid, cell width to ball width ratio 3.00': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [3.0]
        }
    }

# Collision Manager is always Grid, compare performance
# CircleShape vs AARectShape. 
cshape_cases = {
    'Grid, cshape CircleShape, cell to ball 1.25': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [1.25] # desired (cell width) / (obj width) ratio
        },
    'Grid, cshape CircleShape, cell to ball 2.00': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [2.0]
        },
    'Grid, cshape AARectShape, cell to ball 1.25': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['AARectShape'],
        'collman_gen_args': [1.25]
        },
    'Grid, cshape AARectShape, cell to ball 2.00': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['AARectShape'],
        'collman_gen_args': [2.0]
        },
    }


# Collision Manager is always Grid, fixed cell width, see that mixing
# shapes has acceptable performance
cshape_mixed_cases = {
    'only CircleShape s': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape'],
        'collman_gen_args': [1.25] # desired (cell width) / (obj width) ratio
        },
    'only AARectShape s': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['AARectShape'],
        'collman_gen_args': [1.25]
        },
    'mix 50/50 CircleShape & AARectShape s': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape', 'AARectShape'],
        'collman_gen_args': [1.25]
        }
    }
# <--

# --> generic support for comparisons
def benchmark_time_per_frame(cases, base_world_params, stats_params):
    fixed_world_params = dict(base_world_params)
    fixed_world_params.pop('collision_manager')
    fixed_world_params.pop('cshape_cls_names')

    stats_fixed_params = dict(stats_params) 
    ball_quantities = stats_fixed_params.pop('ball_quantities')
    benchmark = {
        'description':
            """
            Time per frame for different CollisionManagers, measured over
            a number of ball quantities.
            The test situation proposes a rectangular world with elastic
            boundaries, and a number of balls that should do elastic
            collisions (not physically accurate).
            The initial condition is uniform distribution of balls in the
            rectangle, and velocity with uniform angle distribution and
            fixed modulus.
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
        'name': 'bouncing balls model time_per_frame',
        'fixed_params': {
            'world': fixed_world_params,
            'stats_acquisition': stats_fixed_params,
            },
        'ball_quantities': ball_quantities,
        'cases':cases,
        }

    stats = {}
    for case_name in cases:
        case_params = cases[case_name]
        world_params = dict(base_world_params)
        random.seed(world_params.pop('seed'))
        world_params['cshape_cls_names'] = case_params['cshape_cls_names']
        
        collman_cls_name = case_params['collman_cls_name']
        collman_cls = getattr(collision_module, collman_cls_name)
        collman_args = []
        if collman_cls_name == 'CollisionManagerGrid':
            cell_width_to_obj_width_ratio = case_params['collman_gen_args'][0]
            d = world_params
            cell_side = 2.0 * d['ball_radius'] * cell_width_to_obj_width_ratio
            collman_args = (0.0, d['world_width'],
                            0.0, d['world_height'],
                            cell_side, cell_side)
        world_params['collision_manager'] = collman_cls(*collman_args)

        times = []

        for quantity in ball_quantities:
            world = m.World(**world_params)
            world.set_actor_quantity(quantity)
            times.append(time_per_frame(stats_fixed_params, world))

        stats[case_name] = times

    #pprint_stats(stats)
    return stats    
        
def time_per_frame(stats_fixed_params, world):
    dt = stats_fixed_params['dt']
    num_frames = stats_fixed_params['num_frames']
    gc.collect()                 
    start_time = time.time()
    for i in range(num_frames):
        world.update(dt)
    gc.collect()
    end_time = time.time()
    return (end_time - start_time) / num_frames

def pprint_stats(stats):
    print("\nstats = {")
    for case in stats:
        res = stats[case]
        print("    %s:"%repr(case))
        print("        [%s, %s, %s,"%(repr(res[0]), repr(res[1]), repr(res[2]))) 
        print("        %s],"%repr(res[3]))
    print("    }")

def plot_benchmark_time_per_frame(ball_quantities, benchmark_results,
                                  title, pic_filename, ymin, ymax):
    import pylab
    fig = pylab.figure(figsize=(7.0, 11.0))  # size in inches
    fig.suptitle(title, fontsize=12)

    #pylab.axis([0.0, 500, -10 * len(benchmark_results), ymax])  # axis extension
    pylab.axis([0.0, 500, ymin , ymax])  # axis extension
    pylab.rc('axes', linewidth=3)     # thickening axes
 
    # axis labels
    pylab.xlabel(r"num balls", fontsize=12, fontweight='bold')
    pylab.ylabel(r"time per frame in ms", fontsize=12, fontweight='bold')

    # plot cases
    x = ball_quantities
    case_names = [ k for k in benchmark_results]
    case_names.sort()
    colors = [ 'b', 'r', 'g', 'm', '#95B9C7', '#EAC117', '#827839' ]
    for case, color in zip(case_names, colors):
        # convert time to ms
        res = [ v*1000 for v in benchmark_results[case]] 
        pylab.plot(x, res, color=color, label=case)

    # show the plot labels
    pylab.legend(loc='lower center')

    #pylab.show() # show the figure in a new window
    pylab.savefig(pic_filename)

# <--

# --> concrete variants

def sample_plot():
    title = '(sample) bouncing balls model - time per frame'
    fname = '@sample_bouncing_balls_time_per_frame.png'

    fast_stats_params = dict(stats_params)
    # let be fast in the sample plot, dont do this for real stats
    fast_stats_params['num_frames'] = 2
    ball_quantities = fast_stats_params['ball_quantities'] 
    stats = benchmark_time_per_frame(collman_cases, base_demo_world_params,
                                     fast_stats_params)    
    plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -50, 150)
    print('\nPloting sample. For fastness a low frame number was chosen,')
    print('so the numbers obtained are incorrect.')
    print('For real runs, use num_frames = 100 .')
    print('Resulting plot saved in file:', fname)

def plot_collman_cases():
    title = 'bouncing balls model - time per frame\n Comparing Collision Manager implementations'
    fname = 'comparing_collision_managers.png'
    print('\nWorking, it will take around five minutes to complete.')

    ball_quantities = stats_params['ball_quantities'] 
    stats = benchmark_time_per_frame(collman_cases, base_demo_world_params,
                                     stats_params)    
    plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -50, 150)
    print('Done. Resulting plot saved in file:', fname)

def plot_cshape_cases():
    title = 'bouncing balls model - time per frame\n Comparing performance over cshapes and cell size'
    fname = 'comparing_shapes.png'
    print('\nWorking, it will take around five minutes to complete.')

    ball_quantities = stats_params['ball_quantities'] 
    stats = benchmark_time_per_frame(cshape_cases, base_demo_world_params,
                                     stats_params)    
    plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -10, 50)
    print('Done. Resulting plot saved in file:', fname)

def plot_mixed_cshape_cases():
    title = 'bouncing balls model - time per frame\n Comparing mixed shapes performance'
    fname = 'comparing_mixed_shapes.png'
    print('\nWorking, it will take around five minutes to complete.')

    ball_quantities = stats_params['ball_quantities'] 
    stats = benchmark_time_per_frame(cshape_mixed_cases, base_demo_world_params,
                                     stats_params)    
    plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -10, 50)
    print('Done. Resulting plot saved in file:', fname)

# <--


if __name__ == '__main__':
    import cocos.collision_model as cm
    __builtins__.collision_module = cm
    #sample_plot()
    #plot_collman_cases() # slow due to brute force case
    #plot_cshape_cases()
    plot_mixed_cshape_cases()

## sample stats output: testbed windows xp sp3 32 bits, python 2.6.5,
## AMD athlon dual core 5200+, memory DDR2 800 single channel
## parameters were:
##    base_demo_world_params = {
##        'seed': 123456,
##        'world_width': 800.0,
##        'world_height': 600.0,
##        'border_thickness': 50.0, 
##        'ball_radius': 16.0,
##        'fastness': 64.0,
##        'k_border': 10.0,
##        'k_ball': 10.0
##        
##        'cshape_cls_names': None # must be filled 'CircleShape' #'AARectShape'
##        'collision_manager': None # must be filled, see below
##        }
##
##    stats_params = {
##        'ball_quantities' = [50, 100, 250, 500],
##        'num_frames': 100,
##        'dt': 1.0 / 60.0
##    }
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
