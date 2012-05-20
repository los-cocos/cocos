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
        'scan_changed',
        'IOerror'
        ]
    text = hl.rpt(db, selectors, verbose=verbose)
    return text

# filename to persist the db
filename_persist = 'initial.dat'
# change the string to identify about which machine is the info collected 
testbed = 'ati 6570'
# dir used to calculate canonical paths
basepath = '../..'
# dir where update_snapshots will store snapshots
snapshots_dir = '../../test/snp'

clean = True
if clean:
    db = hl.new_db(filename_persist)
    hl.new_testbed(db, testbed, basepath)

    all_test_files = doers.files_from_dir('../../test', fn_fname_test_py)
    hl.add_targets(db, filename_persist, all_test_files)
    candidates, unknowns = hl.get_scripts(db, 'all')
    assert len(unknowns)==0
    assert len(candidates)==len(all_test_files)
    
    # scan candidates to get info needed by update snapshots
    scripts, unknowns = hl.update_scan_props(db, filename_persist, candidates)
    assert scripts==candidates

    # select snapshot candidates
    candidates, unknowns = hl.get_scripts(db, 'testinfo_valid')
    assert len(unknowns)==0

    # do snapshots
    scripts, unknowns = hl.update_snapshots(db, filename_persist, candidates,
                                            snapshots_dir)
    assert len(unknowns)==0

else:
    db = dbm.db_load(filename_persist, default_testbed=testbed)

print progress_report(db, verbose=False)
print hl.rpt(db, ['testinfo_invalid'], verbose=True)
print hl.rpt(db, ['IOerror'])
print hl.rpt_detail_diagnostics(db, 'snapshots_failure')
print hl.rpt_detail_diagnostics(db, 'testinfo_invalid')
#print hl.rpt(db, ['snapshots_success'], verbose=True)

