from __future__ import division, print_function, unicode_literals

import sys
msg = """
To run this script you need the package remembercases, which can be found at
https://bitbucket.org/ccanepa/remembercases
Instructions about how to install in the same page.
"""
try:
    import remembercases
except ImportError:
    print(msg)
    sys.exit(1)

import os
import pprint
import pickle
import copy

import remembercases.db as dbm
import helpers as hl


def new(db_fname, testbed, stats_fname, candidates, limit, samples_dir):
    db = dbm.db_load(db_fname, default_testbed=testbed)
    # test stats_fname writable
    with open(stats_fname, 'wb') as f:
        f.write("hello".encode('utf-8'))
    res = hl.measure_repeteability(db, candidates, limit, samples_dir)
    #overal_md5, elapsed, rounds, stats_by_script_name, stats_by_snapshot_name  = res
    session = db_fname, testbed, samples_dir, res
    with open(stats_fname, 'wb') as f:
        pickle.dump(session, f, 2)
        
def load_stats(stats_fname):
    with open(stats_fname, 'rb') as f:
        session = pickle.load(f)
    db_fname, testbed, samples_dir, res = session
    overal_md5, elapsed, rounds, stats_by_script_name, stats_by_snapshot_name  = res
    return (db_fname, testbed, samples_dir,
            overal_md5, elapsed, rounds,
            stats_by_script_name, stats_by_snapshot_name
            )
            
def more_rounds(stats_fname, limit, debug=False):
    """
    Adds more rounds to the stats pointed by stats_fname
    limit : int or float
        int means rounds to run
        float means minutes to run, will be exceded to complete the last run
        debug : for debugging the merge part; normal use is False, meaning
        the new rounds will be done, False means it will try to use the temp
        file generated in a previous more_rounds run
    """
    (db_fname, testbed, samples_dir,
     overal_md5, elapsed, rounds,
     stats_by_script_name, stats_by_snapshot_name
    ) = load_stats(stats_fname)

    candidates = [name for name in stats_by_script_name]
    tmp_stats = stats_fname + '.tmp'
    if debug:
        # use the temp generated in a previous run; typical use is
        # for debug the merge code
        pass
    else:
        new(db_fname, testbed, tmp_stats, candidates, limit, samples_dir)

    # combine both stats
    (db_fname_2, testbed_2, samples_dir_2,
     overal_md5_2, elapsed_2, rounds_2,
     stats_by_script_name_2, stats_by_snapshot_name_2
    ) = load_stats(tmp_stats)
    
    # for paranoid debbuging we should check no mismatch in the spec of both
    # runs, like db_fanme == db_fname2, etc but we will spare that

    elapsed += elapsed_2

    rounds += rounds_2

    for name in stats_by_script_name:
        stats_by_script_name[name]['timeouts'] += stats_by_script_name_2[name]['timeouts']
        stats_by_script_name[name]['errs'] += stats_by_script_name_2[name]['errs']

    for snap in stats_by_snapshot_name:
        d = stats_by_snapshot_name[snap]
        d_2 = stats_by_snapshot_name_2[snap]
        common = [ k for k in d if k in d_2 ]
        for k in common:
            d[k] += d_2[k]
        only_d_2 = [ k for k in d_2 if k not in d ]
        for k in only_d_2:
            d[k] = d_2[k]

    stats_bak = stats_fname + '.bak'
    if os.path.exists(stats_bak):
        os.remove(stats_bak)
    os.rename(stats_fname, stats_bak)
    # save as in new
    res = overal_md5, elapsed, rounds, stats_by_script_name, stats_by_snapshot_name
    session = db_fname, testbed, samples_dir, res
    with open(stats_fname, 'wb') as f:
        pickle.dump(session, f)

    # verify
    with open(stats_fname, 'rb') as f:
        session3 = pickle.load(f)
    assert session3 == session 
    
def expand_stats(db, rounds, stats_by_script_name, stats_by_snapshot_name):

    agregated_stats_by_snap = {}
    for snap in stats_by_snapshot_name:
        d = stats_by_snapshot_name[snap]
        counts = [ d[k] for k in d ]
        taken = sum(counts)
        most_common = max(counts)
        agregated_stats_by_snap[snap] = {
            'taken': taken,
            'most_common': most_common,
            'variants': len(d),
            }

    expaned_stats_by_script_name = copy.deepcopy(stats_by_script_name)
    # add some more stats by script
    for name in expaned_stats_by_script_name:
        d = expaned_stats_by_script_name[name]
        expected_snapshots = db.get_prop_value(name, 'expected_snapshots')
        d['snap_expected'] = rounds * len(expected_snapshots)
        d['snap_taken'] = sum( [ agregated_stats_by_snap[sn]['taken']
                                               for sn in expected_snapshots ])
        d['snap_missings'] = d['snap_expected'] - d['snap_taken']
        d['sum_most_common'] = sum( [ agregated_stats_by_snap[sn]['most_common']
                                               for sn in expected_snapshots ])
        d['repeteable'] = (d['sum_most_common'] == d['snap_expected'])
        d['repeteability'] = d['sum_most_common'] / d['snap_expected']
        d['excess_variants'] = (
            sum( [ agregated_stats_by_snap[sn]['variants'] - 1
                                               for sn in expected_snapshots ]))

    return agregated_stats_by_snap, expaned_stats_by_script_name    

def rpt_compact(elapsed, rounds, res_expand, verbose=False):
    agregated_stats_by_snap, expaned_stats_by_script_name = res_expand
    text_parts = []
    stats = expaned_stats_by_script_name
    num_scripts = len(stats)
    text_parts.append("Total rounds: %d"%rounds)
    text_parts.append("Total time elapsed: %5.1f minutes"%(elapsed / 60))
    t_sec = elapsed / rounds
    text_parts.append("Elapsed time per round: %4.1f minutes"%(t_sec/60))
    text_parts.append("Scripts tested: %d"%num_scripts)
    repeteables = set([ k for k in stats if stats[k]['repeteable']])
    text_parts.append("Totally repeteable scripts: ( %d / %d)"%
                                                (len(repeteables), num_scripts))
    if verbose:
        pass

    wmissings = set([ k for k in stats if stats[k]['snap_missings'] >0 ])
    text_parts.append("Scripts missing some snapshots: ( %d / %d)"%
                                                (len(wmissings), num_scripts))
    if verbose:
        pass

    werror = set([ k for k in stats if stats[k]['errs'] >0 ])
    text_parts.append("Scripts which errored in some run: ( %d / %d)"%
                                                (len(werror), num_scripts))
    if verbose:
        pass

    qrepeteables = set([ k for k in stats if k not in repeteables ])
    text_parts.append("Scripts not perfectly repeteables: ( %d / %d)"%
                                                (len(qrepeteables), num_scripts))
    for name in sorted(qrepeteables):
        text_parts.append('\t%s'%name)

    if verbose:
        pass

    text = '\n'.join(text_parts)
    return text

def report(stats_fname, rpt_function):
    (db_fname, testbed, samples_dir,
     overal_md5, elapsed, rounds,
     stats_by_script_name, stats_by_snapshot_name
    ) = load_stats(stats_fname)

    db = dbm.db_load(db_fname, default_testbed=testbed)

    res_expand = expand_stats(db, rounds, stats_by_script_name, stats_by_snapshot_name)
    text = rpt_function(elapsed, rounds, res_expand, verbose=False)
    return text

# test main
# set hardcoded params

db_fname = 'initial.dat' # must exist as a result of running recon.py
testbed = 'cpu intel E7400, gpu ati 6570 with Catalyst 11-5 drivers, win xp sp3'
stats_fname = 'rep_stats.pkl' 
samples_dir = '../../test/saux'

# for real runs set 'candidates=None' and limit according to how much time
# you can spend in runs.
# To add more rounds to a stats, set clean=False ; it is fine to have
# different limit when adding rounds 
#candidates = ['test/test_accel_amplitude.py', 'test/test_base.py']
candidates = None # means all tests
# debug
#candidates = ['test/test_target.py', 'test/test_sprite_aabb.py']

clean = True # True starts a new stats serie
debug_merge = False # Normal is False, use True to debug combinning stats
#limit = 2 #int means rounds
limit = 20.0 #float means minutes; will be exceeded to complete last round

if clean:
    new(db_fname, testbed, stats_fname, candidates, limit, samples_dir)
else:
    more_rounds(stats_fname, limit, debug=debug_merge)

print(report(stats_fname, rpt_compact))
