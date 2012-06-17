"""
exercise and develop autotest funtionality
"""

import sys
msg = """
To run this script you need the package remembercases, which can be found at
https://bitbucket.org/ccanepa/remembercases
Instructions about how to install in the same page.
"""
try:
    import remembercases
except ImportError:
    print msg
    sys.exit(1)
    
import os
import pprint
import helpers as hl
import remembercases.db as dbm
import remembercases.doers as doers

def fn_fname_test_py(filename):
    return filename.startswith('test_') and filename.endswith('.py')

def progress_report(db, verbose=False):
    selectors = [
        'testinfo_valid',
        'testinfo_invalid',
        'testinfo_missing',
        #'all',
        'snapshots_success',
        'snapshots_failure',
        'IOerror',
        'testrun_pass'
        ]
    text = hl.rpt(db, selectors, verbose=verbose)
    return text


# -- > one-off tasks
def update_1(db, filename_persist):
    """ redo scan + snapshopts for this files """
    text = """

        : update1

        test/test_bezier_direct.py
        test/test_blink.py
        test/test_callfunc.py
        test/test_callfuncs.py
        test/test_camera_orbit.py
        test/test_corner_swap.py 
        test/test_decorator.py
        test/test_fadein.py
        test/test_hide.py
        test/test_hierarchy.py
        test/test_layer_rotate.py
        test/test_loop.py
        test/test_moveby.py
        test/test_moveto.py
        test/test_repeat2.py
        test/test_scene_add_scaled.py
        test/test_togglevisibility.py
        test/test_label_changing.py
    """

    candidates = doers.scripts_names_from_text(text, end_mark=':')

    # scan candidates to get info needed by update snapshots
    candidates, unknowns = hl.update_scanprops(db, filename_persist, candidates)
    assert len(unknowns) == 0

    # do snapshots
    candidates, unknowns = hl.update_snapshots(db, filename_persist, candidates,
                                            snapshots_dir)
    li = list(candidates)
    li.sort()
    text_history = '\n'.join(li)

    assert len(unknowns)==0
    db.history_add("updated tests and snapshots", text_history)
    dbm.db_save(db, filename_persist)

def update_2(db, filename_persist, snapshots_dir):
    """ redo scan + snapshopts for this files """
    text = """

        : update2

        test/test_camera_orbit.py
        test/test_fadein.py
    """

    candidates = doers.scripts_names_from_text(text, end_mark=':')

    # scan candidates to get info needed by update snapshots
    candidates, unknowns = hl.update_scanprops(db, filename_persist, candidates)
    assert len(unknowns) == 0

    # do snapshots
    candidates, unknowns = hl.update_snapshots(db, filename_persist, candidates,
                                            snapshots_dir)
    li = list(candidates)
    li.sort()
    text_history = '\n'.join(li)

    assert len(unknowns)==0
    db.history_add("updated tests and snapshots", text_history)
    dbm.db_save(db, filename_persist)

def update_3(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder
    """
    text = """
        : Snapshots inspected, 'pass'

        test/test_accel_amplitude.py
        test/test_accel_deccel_amplitude.py
        test/test_acceldeccel.py
        test/test_accelerate.py
        test/test_accelerate_speed.py
        test/test_anchor_sprites.py
        test/test_anchors.py
        test/test_animation.py
        test/test_base.py
        test/test_batch.py
        test/test_batch3.py
        test/test_bezier.py
        test/test_camera_orbit_reuse.py
        test/test_camera_orbit_with_grid.py
        test/test_compose.py
        test/test_draw_elbows.py
        test/test_draw_elbows2.py
        test/test_draw_endcaps.py
        test/test_draw_line.py
        test/test_draw_parameter.py
        test/test_draw_pushpop.py
        test/test_draw_rotate.py
        test/test_fadeout.py
        test/test_fadeout_layer.py
        test/test_fadeouttiles_bl.py
        test/test_fadeouttiles_down.py
        test/test_fadeouttiles_tr.py
        test/test_fadeouttiles_up.py
        test/test_flip.py
        test/test_flip_x.py
        test/test_flip_x_3d.py
        test/test_flip_y.py
        test/test_flip_y_3d.py
        test/test_fluent.py
        test/test_hierarchy2.py
        test/test_htmllabel.py
        test/test_htmllabel_opacity.py
        test/test_jump.py
        test/test_label.py
        test/test_label_opacity.py
        test/test_layeractions.py
        test/test_layersublayer.py
        test/test_lerp.py
        test/test_place.py
        test/test_remove.py
        test/test_repeat.py
        test/test_rich_label.py
        test/test_rotate.py
        test/test_rotateto.py
        test/test_scaleby.py
        test/test_scaleby2.py
        test/test_scaleto.py
        test/test_scene_add_rotated.py
        test/test_scene_add_translated.py
        test/test_scene_rotate.py
        test/test_scene_scale.py
        test/test_sceneactions.py
        test/test_sequence.py
        test/test_sequence1.py
        test/test_sequence2.py
        test/test_sequence3.py
        test/test_sequence4.py
        test/test_sequence5.py
        test/test_sequence6.py
        test/test_show.py
        test/test_shuffletiles.py
        test/test_shuffletiles_fullscreen.py
        test/test_shuffletiles_reverse.py
        test/test_skeleton.py
        test/test_spawn.py
        test/test_speed.py
        test/test_sprite.py
        test/test_wavestiles3d.py
        test/test_wavestiles3d_fullscreen.py
        test/test_wavestiles3d_reversed.py

        : Second round
        test/test_bezier_direct.py : changed code for better snapshot
        test/test_blink.py : changed test, changed library code
        test/test_callfunc.py
        test/test_callfuncs.py
        test/test_corner_swap.py 
        test/test_decorator.py
        test/test_hide.py
        test/test_hierarchy.py
        test/test_layer_rotate.py
        test/test_loop.py
        test/test_moveby.py
        test/test_moveto.py
        test/test_repeat2.py
        test/test_scene_add_scaled.py : agregue z explicito porque color layer no se veia en interactivo
        test/test_togglevisibility.py

        : third round
        test/test_fadein.py
        """

    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    checked = [ k for k in checked_in ]
    checked.sort()
    text_hystory = doers.pprint_to_string(checked)
    db.history_add("updated testrun pass", text)
    dbm.db_save(db, filename_persist)

    return checked_in, unknown, move_failed


# <-- one-off tasks



# filename to persist the db
filename_persist = 'initial.dat'
# change the string to identify about which machine is the info collected 
testbed = 'ati 6570'
# dir used to calculate canonical paths
basepath = '../..'
# dir where update_snapshots will store snapshots
snapshots_dir = '../../test/snp'
# dir where reference snapshots will be stored
snapshots_reference_dir = '../../test/ref'

clean = False
if clean:
    db = hl.new_db(filename_persist)
    hl.new_testbed(db, testbed, basepath)

    all_test_files = doers.files_from_dir('../../test', fn_fname_test_py)
    hl.add_targets(db, filename_persist, all_test_files)
    candidates, unknowns = hl.get_scripts(db, 'all')
    assert len(unknowns)==0
    assert len(candidates)==len(all_test_files)
    
    # scan candidates to get info needed by update snapshots
    scripts, unknowns = hl.update_scanprops(db, filename_persist, candidates)
    assert scripts==candidates

    # select snapshot candidates
    candidates, unknowns = hl.get_scripts(db, 'testinfo_valid')
    assert len(unknowns)==0

    # do snapshots
    scripts, unknowns = hl.update_snapshots(db, filename_persist, candidates,
                                            snapshots_dir)
    assert len(unknowns)==0

    # redo scan testinfo + take snapshots due to code editions
    # update_1(db, filename_persist, snapshots_dir)
    # update_2(db, filename_persist, snapshots_dir)
    
    # asses these tests pass human inspection; store snapshots for reference
    update_3(db, filename_persist, snapshots_dir, snapshots_reference_dir)

else:
    db = dbm.db_load(filename_persist, default_testbed=testbed)

print progress_report(db, verbose=False)
##print hl.rpt(db, ['testinfo_invalid'], verbose=True)
##print hl.rpt(db, ['IOerror'])
##print hl.rpt_detail_diagnostics(db, 'snapshots_failure')
##print hl.rpt_detail_diagnostics(db, 'testinfo_invalid')
##print hl.rpt(db, ['snapshots_success'], verbose=True)
#pprint.pprint(db.db)

    

