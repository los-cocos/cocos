from __future__ import division, print_function, unicode_literals

"""Check changes in autotest snapshots

Output:
    scripts, clasified in Snapshots equals, Snapshots differs, Unknown scripts

returncode:
    0 snapshots with current code are the same as in reference snapshots
    1 current code produces different snapshots than in reference snapshots
"""
import sys
import os

import remembercases.db as dbm
import remembercases.doers as doers 
import remembercases.image_comparison as imc
import helpers as hl

# filename to persist the db
filename_persist = 'initial.dat'
# change the string to identify about which machine is the info collected 
#testbed = 'ati 6570'
testbed = 'cpu intel E7400, gpu ati 6570 with Catalyst 11-5 drivers, win xp sp3'
### dir used to calculate canonical paths
##basepath = '../..'
### dir where update_snapshots will store snapshots
##snapshots_dir = '../../test/snp'
# dir where reference snapshots will be stored
snapshots_reference_dir = '../../test/ref'
# dir for some helper tasks
samples_dir = '../../test/saux'

# snapshots comparison parameters
fn_snapshots_dist = imc.distance_01
threshold = 0
tries = 5

### issue 164
##text = """
##        test/test_accel_amplitude.py
##        test/test_accel_deccel_amplitude.py
##        test/test_camera_orbit.py
##        test/test_camera_orbit_reuse.py
##        test/test_camera_orbit_with_grid.py
##        test/test_corner_swap.py
##        test/test_fadeouttiles_bl.py
##        test/test_fadeouttiles_down.py
##        test/test_fadeouttiles_tr.py
##        test/test_fadeouttiles_up.py
##        test/test_flip.py
##        test/test_flip_x.py
##        test/test_flip_x_3d.py
##        test/test_flip_y.py
##        test/test_flip_y_3d.py
##        test/test_grid_effect_in_sprite.py
##        test/test_jumptiles3d.py
##        test/test_lens_3d.py
##        test/test_liquid_16_x_16.py
##        test/test_move_corner_down.py
##        test/test_move_corner_up.py
##        test/test_multiple_grid_effects.py
##        test/test_quadmoveby.py
##        test/test_reuse_grid.py
##        test/test_reverse_time.py
##        test/test_ripple3d.py
##        test/test_shaky3d.py
##        test/test_shakytiles3d.py
##        test/test_shattered_tiles_3d.py
##        test/test_shuffletiles.py
##        test/test_shuffletiles_fullscreen.py
##        test/test_shuffletiles_reverse.py
##        test/test_skew_horizontal.py
##        test/test_skew_vertical.py
##        test/test_stop_grid.py
##        test/test_transition_corner_move.py
##        test/test_transition_envelope.py
##        test/test_transition_fade.py
##        test/test_transition_fadebl.py
##        test/test_transition_fadetr.py
##        test/test_transition_fadeup.py
##        test/test_transition_flipx.py
##        test/test_transition_flipy.py
##        test/test_transition_flip_angular.py
##        test/test_transition_jumpzoom.py
##        test/test_transition_movein_t.py
##        test/test_transition_rotozoom.py
##        test/test_transition_shrink_grow.py
##        test/test_transition_shuffle.py
##        test/test_transition_slidein_l.py
##        test/test_transition_splitcols.py
##        test/test_transition_splitrows.py
##        test/test_transition_turnofftiles.py
##        test/test_transition_zoom.py
##        test/test_turnoff_tiles.py
##        test/test_twirl.py
##        test/test_waves.py
##        test/test_waves3d.py
##        test/test_wavestiles3d.py
##        test/test_wavestiles3d_fullscreen.py
##        test/test_wavestiles3d_reversed.py
##        test/test_waves_horizontal.py
##        test/test_waves_vertical.py
##    """

#debug
text = """
        test/test_sprite.py
        test/test_base.py
        test/test_subscene_events.py
       """

text =  """
        test/test_action_non_interval.py
        test/test_animation.py
        test/test_rect.py
        test/test_scrolling_manager_without_tiles.py
        test/test_scrolling_manager_without_tiles_autoscale.py
        test/test_tiles_autotest.py
        test/test_tmx_autotest.py
        """

# sanity checks
diagnostic = ''
if not os.path.exists(snapshots_reference_dir):
    diagnostic = "Snapshots references dir not found:%s"%snapshots_reference_dir

db = dbm.db_load(filename_persist, default_testbed=testbed)
##knowns, unknowns = db.entities(fn_allow=hl.fn_allow_testrun_pass, candidates=None)

candidates = doers.scripts_names_from_text(text, end_mark=':')
knowns, unknowns = db.entities(fn_allow=None, candidates=candidates)
if unknowns:
    msg = '\n'.join(unknowns)
    diagnostic = "Unknown scripts:\n" + msg

if diagnostic:
    sys.stderr.write(diagnostic)
    sys.exit(1)

# payload
equals, unequals, untested = hl.snapshots_compare(db, fn_snapshots_dist,
                                                  threshold, knowns, tries,
                                                  snapshots_reference_dir,
                                                  samples_dir)
# output
msg = ''
if equals:
    tmp = doers.join_sorted(equals)
    msg = msg + '\n: Snapshots equals\n\n' + tmp

if unequals:
    tmp = doers.join_sorted(unequals)
    msg = msg + '\n\n: Snapshots differs\n\n' + tmp

if untested:
    tmp = doers.join_sorted(untested)
    msg = ( msg + '\n\n' +
            ": Untested (unknown, bad testinfo or don't want sanapshots)\n\n" +
            tmp )

sys.stdout.write(msg)

if not unequals and not unknowns:
    returncode = 0
else:
    returncode = 1

sys.exit(returncode)
