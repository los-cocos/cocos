"""
exercise and develop autotest funtionality
"""

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
        'testrun_pass',
        'testrun_not_pass',
        'not_inspected', 
        'testrun_present',
        'outdated_weak',
        ]
    text = hl.rpt(db, selectors, verbose=verbose)
    return text


# -- > one-off tasks

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

    return checked_in, unknown, move_failed


##def update_5(db, filename_persist, snapshots_dir):
##    """ re-(scan + snapshot) for this files"""
##    text = """
##         test/test_SequenceScene.py
##         test/test_lens_3d.py
##         test/test_fadeto.py
##         test/test_grid_effect_in_layer.py
##         test/test_grid_effect_in_sprite.py
##         test/test_particle_explosion.py
##         test/test_particle_fire.py
##         test/test_particle_fireworks.py
##         test/test_particle_flower.py
##         test/test_particle_galaxy.py
##         test/test_particle_meteor.py
##         test/test_particle_smoke.py
##         test/test_particle_spiral.py
##         test/test_transition_jumpzoom.py
##         test/test_transition_rotozoom.py
##         """
##    candidates = doers.scripts_names_from_text(text, end_mark=':')
##    hl.re_scan_and_shoot(db, filename_persist, candidates, snapshots_dir)

def update_6(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder
    """
    text = """
        : Snapshots inspected, 'pass'

        test/test_cocosz.py
        test/test_delay.py
        test/test_draw.py
        test/test_liquid_16_x_16.py
        test/test_move_corner_down.py
        test/test_move_corner_up.py
        test/test_multiple_grid_effects.py
        test/test_transition_corner_move.py
        test/test_transition_envelope.py
        test/test_transition_fade.py
        test/test_transition_fadebl.py
        test/test_transition_fadetr.py
        test/test_transition_fadeup.py
        test/test_transition_flip_angular.py
        test/test_transition_flipx.py
        test/test_transition_flipy.py
        test/test_transition_movein_t.py
        test/test_transition_shrink_grow.py
        test/test_transition_shuffle.py 
        test/test_transition_slidein_l.py
        test/test_transition_splitcols.py
        test/test_transition_splitrows.py
        test/test_transition_turnofftiles.py
        test/test_quadmoveby.py
        test/test_reuse_grid.py
        test/test_reverse.py
        test/test_reverse_time.py
        test/test_ripple3d.py
        test/test_shader.py
        test/test_shaky3d.py
        test/test_shakytiles3d.py
        test/test_shattered_tiles_3d.py
        test/test_skeleton_anim.py
        test/test_skeleton_bitmap_skin.py
        test/test_skew_horizontal.py
        test/test_skew_vertical.py
        test/test_sprite_aabb.py
        test/test_stop_grid.py
        test/test_transform_anchor.py
        test/test_turnoff_tiles.py
        test/test_twirl.py
        test/test_waves.py
        test/test_waves3d.py
        test/test_waves_horizontal.py
        test/test_waves_vertical.py
        test/test_world_coordinates.py
        test/test_fadeto.py
        test/test_grid_effect_in_layer.py
        test/test_grid_effect_in_sprite.py
        test/test_transition_jumpzoom.py
        test/test_lens_3d.py
        test/test_transition_rotozoom.py
        """

    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    return checked_in, unknown, move_failed


##def update_7(db, filename_persist):
##    """add new tests"""
##    text = """
##        test/test_schedule_interval.py : new, svn add done
##        test/test_aspect_ratio_on_resize.py : new, svn add done
##        """
##    candidates = doers.scripts_names_from_text(text, end_mark=':')
##    hl.add_entities(db, filename_persist, candidates)
##    db.history_add("added tests", text)
##    dbm.db_save(db, filename_persist)

def update_9(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder
    """
    text = """
        test/test_action_non_interval.py
        test/test_all_collisions.py : puede no ser representativo; agregado z para ver si cuadrado rinde
        test/test_draw_resolution.py
        test/test_interpreter_layer.py : weak test, interpreter not exercised
        test/test_menu_bottom_right.py : todos los de menu no prueban automaticamente la logica
        test/test_menu_centered.py
        test/test_menu_fixed_position.py
        test/test_menu_items.py
        test/test_menu_rotated.py
        test/test_menu_top_left.py
        test/test_particle_explosion.py
        test/test_particle_fire.py
        test/test_particle_fireworks.py
        test/test_particle_flower.py
        test/test_particle_galaxy.py
        test/test_particle_meteor.py
        test/test_particle_smoke.py
        test/test_particle_spiral.py
        test/test_particle_sun.py
        test/test_schedule.py
        test/test_unscaled_win_resize.py
    """
    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    return checked_in, unknown, move_failed

##def update_10(db, filename_persist, snapshots_dir):
##    """ delete this entities, they were added with wrong path"""
##    text = """
##        tools/autotest/test/test_aspect_ratio_on_resize.py
##        tools/autotest/test/test_schedule_interval.py
##        tools/autotest/test_aspect_ratio_on_resize.py
##         """
##    candidates = doers.scripts_names_from_text(text, end_mark=':')
##    for name in candidates:
##        db.del_entity(name)
##    db.history_add("deleted unwanted entities", text)
##    dbm.db_save(db, filename_persist)

##def update_11(db, filename_persist, snapshots_dir):
##    """ Reflect some test renames (added but without testinfo): delete, add
##        If there were snapshots or testrun props more caoutious aproach is
##        needed"""
##    
##    text1 = """
##        test/test_rotate_move_reverse.py
##        test/test_local_coordinates.py
##         """
##    candidates = doers.scripts_names_from_text(text1, end_mark=':')
##    for name in candidates:
##        db.del_entity(name)
##
##    text2 = """
##        test/test_rotate_reverse.py
##        test/test_rect.py
##        """
##    candidates = doers.scripts_names_from_text(text2, end_mark=':')
##    hl.hl.add_entities(db, filename_persist, candidates)
##
##    text = text1 + '\nto\n' + text2
##    db.history_add("renamed entities", text)
##    dbm.db_save(db, filename_persist)


def update_19(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder
    """
    text = """
        test/test_aspect_16_9_to_fullscreen.py
        test/test_aspect_4_3_to_fullscreen.py
        test/test_aspect_ratio_on_resize.py
        test/test_coords.py
        test/test_custom_on_resize.py
        test/test_entry_menu_item.py
        test/test_handler.py
        test/test_multiplex_layer.py
        test/test_parallax.py
        test/test_platformer.py
        test/test_rect.py
        test/test_rotate_reverse.py
        test/test_scrolling_manager_without_tiles.py
        test/test_scrolling_manager_without_tiles_autoscale.py
        test/test_tiles.py
        test/test_tiles_autotest.py
        test/test_tmx.py
        test/test_tmx_autotest.py
        test/test_schedule_actions.py
        test/test_target.py
        test/test_sublayer_events.py
        test/test_subscene_events.py
    """
    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    return checked_in, unknown, move_failed

def update_21(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder
    """
    text = """
        test/test_label_changing.py
        test/test_batch2.py
        test/test_scalexy.py
        test/test_shader_examples.py
    """
    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    return checked_in, unknown, move_failed


def update_22(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    Enter testrun info 'fail' or 'error' for some tests
    
    'fail' : The test is properly writen to demo some feature and snapshots
    reflects what is seen in an interactive session but the images show the
    feature renders in an undesired way. This point to a library error.

    'error' : The test is inconclusive about correctnes in the library,
    because they are one or many of the following problems:

        Test is not properly writen (logical errors in the test code)
        
        Technical problems with the snapshots machinery ( the snapshots don't
        reflect an interactive session )

        Snapshots not repeteable in different test runs.
    """
    data = {
      # 'fail'
      'test/test_pyglet_vb.py' : {
        'st': 'fail', 'diag': 'incomplete grossini rendition at first frame'},

      # 'error'
      'test/test_text_movement.py' : {
        'st': 'error',
        'diag': 'position should be set at the node level, not at the element level'},

      'test/test_schedule_interval.py' : {
          'st':'error', 'diag': 'bad timestamps, repeated snapshots'},

      'test/test_transitions_with_pop_recipe.py' : {
          'st':'error', 'diag': 'bad timestamps, repeated snapshots'},

      'test/test_SequenceScene.py' : {
          'st':'error', 'diag': 'bad timestamps, black frame'},

      'test/test_camera_orbit.py' : {
          'st':'error', 'diag': 'alternate snapshots are pure black'},

      'test/test_jumptiles3d.py' : {
          'st':'error', 'diag': "snpshots don't folow changes in scene"},

      'test/test_transition_zoom.py' : {
          'st':'error', 'diag': 'bad timestamps, repeated snapshots'},
      }

    ren_key = {'st':'testrun_success', 'diag':'testrun_diagnostic'}
    testrun_props_by_candidate = {}
    for name in data:
        testrun_props_by_candidate[name] = dict([(ren_key[k], data[name][k]) for k in data[name]])
    
    hl.update_testrun__bad(db, filename_persist, testrun_props_by_candidate,
                           snapshots_dir, snapshots_reference_dir)

def update_23(db, filename_persist, snapshots_dir, snapshots_reference_dir):
    """
    This files 'pass', register them as such and move their snapshots
    to the reference snapshots folder (but the second script should be
    updated for better autotest)
    """
    text = """
        test/test_fadeto.py
        test/test_draw_elbows2.py
    """
    candidates = doers.scripts_names_from_text(text, end_mark=':')
    checked_in, unknown, move_failed = hl.update_testrun__pass(db,
                                        filename_persist, candidates,
                                        snapshots_dir, snapshots_reference_dir)    

    return checked_in, unknown, move_failed



# <-- one-off tasks


# filename to persist the db
filename_persist = 'initial.dat'
# change the string to identify about which machine is the info collected 
testbed = 'cpu intel E7400, gpu ati 6570 with Catalyst 11-5 drivers, win xp sp3'
# dir used to calculate canonical paths
basepath = '../..'
# dir where update_snapshots will store snapshots
snapshots_dir = '../../test/snp'
# dir where reference snapshots will be stored
snapshots_reference_dir = '../../test/ref'
# dir for some helper tasks
samples_dir = '../../test/saux'

clean = True
if clean:
    # updates commented out were used in the initial buildup, there are no
    # longer neccesary in a clean build but are keep (comented out) to
    # hint possible opers. Maintenace will need some of them.
    db = hl.new_db(filename_persist)
    hl.new_testbed(db, testbed, basepath)

    # add all scripts test_*.py as entities
    all_test_files = doers.files_from_dir('../../test', fn_fname_test_py)
    canonical_names = hl.canonical_names_from_filenames(db, all_test_files)
    hl.add_entities(db, filename_persist, canonical_names)
    candidates, unknowns = hl.get_scripts(db, 'all')
    assert len(unknowns)==0
    assert candidates == set(canonical_names)
    
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
    
    # asses these tests pass human inspection; store snapshots for reference
    update_3(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # redo scan + snapshots due to test editions
    #update_5(db, filename_persist, snapshots_dir)

    # asses these tests pass human inspection; store snapshots for reference
    update_6(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # add some newly writen tests
    #update_7(db, filename_persist)

    # asses these tests pass human inspection; store snapshots for reference
    update_9(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # erasing some wrong entered entities
    #update_10(db, filename_persist, snapshots_dir)

    # renaming some tests added but without testinfo (delete + add)
    #update_11(db, filename_persist, snapshots_dir)

    # asses these tests pass human inspection; store snapshots for reference
    update_19(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # asses these tests pass human inspection; store snapshots for reference
    update_21(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # asses these tests have problems
    update_22(db, filename_persist, snapshots_dir, snapshots_reference_dir)

    # asses these tests pass human inspection; store snapshots for reference
    update_23(db, filename_persist, snapshots_dir, snapshots_reference_dir)

else:
    db = dbm.db_load(filename_persist, default_testbed=testbed)

# a concise status report
print(progress_report(db, verbose=False))

### list tests with bad testinfo
##print(hl.rpt(db, ['testinfo_invalid'], verbose=True))
##
### details for tests with bad testinfo, including diagnostic
##print(hl.rpt_detail_diagnostics(db, 'testinfo_invalid'))
##
##
### entities with no props, it can be 'added but not scaned' or 'added with
### wrong name'
###print(hl.rpt(db, ['no_props'], verbose=True))
##
### tests that don't have testinfo at all
##print(hl.rpt(db, ['testinfo_missing'], verbose=True))
##
### tests that can't be readed, probably due to name mismatch 
### print(hl.rpt(db, ['IOerror']))
##
# print detailed info about test that tried but failed to take snapshots
print(hl.rpt_detail_diagnostics(db, 'snapshots_failure'))
##
### lists test that took snapshots without technical problems
####print(hl.rpt(db, ['snapshots_success'], verbose=True))
##
# dump the entire db to console
#pprint.pprint(db.db)
##
### show all props for a given entity
###entity = 'test/test_unscaled_win_resize.py'
#print(hl.rpt_all_props(db, ['test/test_schedule_interval.py']))
##
### list all tests that have valid testinfo and don't have testrun_success=='pass'
print(hl.rpt(db, ['testrun_not_pass'], verbose=True))

# list all tests that have been inspected ( ie have 'testrun_success' prop )
#print(hl.rpt(db, ['testrun_present'], verbose=True))

# list all test outdated (this is weak, because no re-scan is performed.
# for a strong ouddated, make a scan before calling the weak outdated
#print(hl.rpt(db, ['outdated_weak'], verbose=True))

### tests that have testinfo and dont have testun info
##print(hl.rpt(db, ['not_inspected'], verbose=True))

### tests with testrun outdated (strong version)
##print(hl.rpt_testrun_outdated_strong(db))

# report differences between 1st iterative testbed and a clean build
#print(hl.rpt_compare_testbeds_by_entities('initial_orig.dat', 'ati 6570',
#                                'initial_clean.dat', 'ati 6570', verbose=False))

