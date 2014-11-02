"""
script to compare collision performance between two implementations

Typical use
-----------
    - Intended to run inplace from a cocos checkout, that is, from
      (checkout)/benchmarks/collision
    - copy to that dir the cocos_model.py implementations to compare, with a
      suitable rename; by example collision_0_6.py and collision_joePR.py
    - edit the 'implementations' dict to match the names and the description
    - uncomment the desired comparison
    - run the script
"""
from __future__ import division, print_function, unicode_literals

import imp
import pprint

import a0_benchmark_time_per_frame as cmark 

# --> specify comparison variants
# each variant is a dict specifing the cases to compare

# how to specify cases ('placeholder' would be replaced with implementation_shortname
##cases = {
##    'placeholder': {
##        'collman_cls_name':'hjhjg',
##        'cshape_cls_names': ['dsdas'],
##        'collman_gen_args': [...]
##        }
##    }

# Collision Manager is Grid, cshape is CirclerShape; comparing implementations
# of cocos.collision_model.
implementation_cases_circle = {
    'placeholder': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['CircleShape',],
        'collman_gen_args': [1.25] # desired (cell width) / (obj width) ratio
        },
    }
    
# Collision Manager is Grid, cshape is CirclerShape; comparing implementations
# of cocos.collision_model.
implementation_cases_aa_rect = {
    'placeholder': {
        'collman_cls_name': 'CollisionManagerGrid',
        'cshape_cls_names': ['AARectShape',],
        'collman_gen_args': [1.25] # desired (cell width) / (obj width) ratio
        },
    }

# <--

def time_per_frame_across_implementations(implementations, variant):
    stats = {}
    for case_name in implementations:
        module_name = implementations[case_name]
        cm = __import__(module_name, globals, locals)
        __builtins__.collision_module = cm
        partial_stats = cmark.benchmark_time_per_frame(
                                        variant,
                                        cmark.base_demo_world_params,
                                        cmark.stats_params)
        stats[case_name] = partial_stats['placeholder']
    return stats
    
def plot_implementation_cases_circle(implementations):
    title = 'bouncing balls model - time per frame\n comparing CircleShape implementations'
    fname = 'comparing_circleshape_implementations.png'
    print('\nWorking, it will take around five minutes to complete.')

    ball_quantities = cmark.stats_params['ball_quantities'] 
    stats = time_per_frame_across_implementations(implementations,
                                                  implementation_cases_circle)
    cmark.plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -10, 50)
    print('Done. Plot saved in file:', fname)

def plot_implementation_cases_aa_rect(implementations):
    title = 'bouncing balls model - time per frame\n comparing AARectShape implementations'
    fname = 'comparing_aarectshape_implementations.png'
    print('\nWorking, it will take around five minutes to complete.')

    ball_quantities = cmark.stats_params['ball_quantities'] 
    stats = time_per_frame_across_implementations(implementations,
                                                  implementation_cases_aa_rect)
    cmark.plot_benchmark_time_per_frame(ball_quantities, stats, title, fname, -10, 50)
    print('Done. Plot saved in file:', fname)

        
if __name__ == "__main__":

    # <implementation shortname>: <module name>
    implementations = {
        "cocos 0.6.0": "collision_0_6",
        "collision_dan": "collision_dan"
        }
    try:
        #plot_implementation_cases_circle(implementations)
        plot_implementation_cases_aa_rect(implementations)
    except ImportError as e:
        print('\n***ImportError:', e, '\n')
        print(__doc__)

