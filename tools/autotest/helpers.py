import sys
import os
import re
import itertools as ito
import copy

import remembercases.db as dbm
import remembercases.doers as doers
import remembercases.snapshot_taker as st
import remembercases.proxy as proxy

#>>> helpers to define script props by matching strings in the script's text

def text_props_simple(text, propnames):
    """
    calculate several props from the text and return into a dictionary
    with key the prop name and value the one calculted from text for this prop
    """
    propdict = {}
    for name in propnames:
        func = getattr(sys.modules[text_props_simple.__module__], name)
        propdict[name] = func(text)
    return propdict


c_rgx_timedependent = re.compile(r"""(time)|(action)|(schedule)""", re.MULTILINE)
def timedependent(text):
    return c_rgx_timedependent.search(text) is not None

c_rgx_on_something = re.compile(r""" on_([a-z_]+)""", re.MULTILINE)
def interactive(text):
    n = 0
    while 1:
        match = c_rgx_on_something.search(text, n)
        if match is not None and match.group() in [' on_enter', ' on_exit']:
            n = match.end()
        else:
            break
    return match is not None

def uses_random(text):
    return text.find('random') > -1

def has_testinfo(text):
    return text.find('testinfo') > -1

c_rgx_testinfo = re.compile(r"""^testinfo\s*=\s*(\".*)$""", re.MULTILINE)
def testinfo_payload(text):
    match = c_rgx_testinfo.search(text)
    if match is None:
        return None
    tinfo = match.group(1)
    tinfo = tinfo[1:tinfo.find('"', 1)]
    tinfo = str(tinfo)
    return tinfo

# >>> high level tasks

def new_db(filename_persist):
    """
    Instantiates a new db, saving to filename_persist file.
    RW is exercised on the empty db to ensure no problems with the filename
    """
    if os.path.exists(filename_persist):
        raise ValueError("initial_recon refuses to overwrite an existing file: %s", filename_persist)
    db = dbm.TestbedEntityPropDB()
    dbm.db_save(db, filename_persist)
    new = dbm.db_load(filename_persist)
    return db

def new_testbed(db, testbed, basepath):
    """
    Creates a new testbed in the db with the given basepath, and sets it as the db's default_testbed

    basepath is stored in the testbed, entities that are files should be named
    in canonical form: by the path relative to testbed's basepath.

    A number of props are added to db's testbed.
    """
    db.add_testbed(testbed, basepath)
    db.set_default_testbed(testbed)

    default_groups = {
        "scan" : [
            # script can't be loaded
            'IOerror',
            
            # hints behavior, based on script's text
            'timedependent',
            'interactive',
            'uses_random',
            'has_testinfo', # string 'testinfo' present, maybe theres a real testinfo

            # secondary behavior hints, combination of above
            'static',

            # testinfo
            'testinfo',
            'expected_snapshots',
            'testinfo_diagnostic',
            'md5_at_testinfo',
            ],
        
        "snapshots_capture": [
            'snapshots_success',
            'snapshots_diagnostic',
            'missing_snapshots',
            ],
        
        "testrun": [
            'testrun_success', # 'pass', 'fail', 'error'
            'testrun_diagnostic',
            'testrun_md5'
            ]
        }
    
    for groupname in default_groups:
        db.add_group(groupname, default_groups[groupname], addprops=True)

    # add to history
    text_history = ("testbed: %s\n basepath: %s\nprops:"%(testbed, basepath) +
                    "not implemented")
    db.history_add("new_testbed", text_history)

def add_targets(db, filename_persist, targets):
    scripts = []
    for fname in targets:
        entity = db.canonical_fname(fname)
        db.add_entity(entity)
        scripts.append(entity)
    db.history_add('add_targets','\n'.join(scripts))
    dbm.db_save(db, filename_persist)

def scanprops_from_text(text, fname):
    base_text_props = [
        'timedependent',
        'interactive',
        'uses_random',
        'has_testinfo',
        ]

    if text is None:
        propdict = {'IOerror': True}
        return propict

    # get the props that are simple string matchs in text
    propdict = text_props_simple(text, base_text_props)

    # calc additional props mixing the traits discovered above
    propdict['static'] = ( not propdict['timedependent'] and
                            not propdict['interactive'] )

    # testinfo related props
    testinfo = testinfo_payload(text)
    if testinfo is not None:
        propdict['testinfo'] = testinfo
        basename = os.path.basename(fname)
        diagnostic, expected_snapshots = st.ScreenSampler.validated_info(testinfo, basename)
        propdict['testinfo_diagnostic'] = diagnostic 
        propdict['expected_snapshots'] = expected_snapshots
        propdict['md5_at_testinfo'] = doers.md5_hex(text)

    return propdict

def scanprops_from_fname(fname):
    try:
        text = doers.load_text(fname)
    except:
        text = None
    return scanprops_from_text(text, fname)        

def update_scanprops(db, filename_persist, candidates):
    """
    For each script in candidates the props in 'scan' group are calculated and
    stored as script props.

    candidates should be known entities in the db
    """
    
    known_scripts, unknowns = db.entities(candidates=candidates)

    for script in known_scripts:
        fname = db.fname_from_canonical(script)
        scanprops = scanprops_from_fname(fname)
        db.set_groupdict(script, 'scan', scanprops)

    # update history
    text = '\n'.join(known_scripts)
    db.history_add('update_scan_props', text)

    dbm.db_save(db, filename_persist)
    return known_scripts, unknowns


def update_snapshots(db, filename_persist, target_scripts, snapshots_dir):
    """
    Runs each of the target_scripts, doing:
        screen snapshots as specified by their testinfo.
        snapshots related info is stored in the db under the props
            'snapshots_success': bool
            'snapshots_diagnostic': string; '' no errors, else description of
            failure while trying to take snapshots
            'missing_snapshots': list of missing snapshots filenames

    Parameters:
        db: a remembercases.TestbedEntityPropDB object
        target_scripts: iterable giving script names in db canonical form
        snapshots_dir: string , path to dir to store snapshots

    Preconditions:
        db has set it default_testbed (only the default testbed data will change)
        script names in db canonical form, and are entities in the testbed
        script names has set the props (usualy by call to update_testinfo)
            'testinfo'
            'expected_snapshots'
        snapshot related keys had been deleted to not have stale info on
        failure (usually update_testinfo acomplishes that)

    OUTDATED ^
    """
    proxy_abspath = os.path.abspath('proxy_snapshots.py')
    if not os.path.exists(proxy_abspath):
        raise ValueError("proxy script not found:%s"%proxy_abspath)

    snapshots_abspath = os.path.abspath(snapshots_dir)
    if not os.path.exists(snapshots_abspath):
        os.makedirs(snapshots_abspath)
        
    known_scripts, unknowns = db.entities(candidates=target_scripts)
    
    for script in known_scripts:
        # get the exercise plan
        stored_testinfo = db.get_prop_value(script, 'testinfo')

        # delete old snapshots if they exist
        expected_snapshots = db.get_prop_value(script, 'expected_snapshots')
        for name in expected_snapshots:
            p = os.path.join(snapshots_abspath, name)
            if os.path.exists(p):
                os.remove(p)
        
        # exercise the script acording to testinfo, snapshots would be taken 
        fname = db.fname_from_canonical(script)
        timeout_hit, err = proxy.proxy_run(proxy_abspath, fname, [stored_testinfo, snapshots_abspath])

        # calc and store missing_snapshots prop
        missing = [ s for s in expected_snapshots if not os.path.exists(os.path.join(snapshots_abspath, s))]
        db.set_prop_value(script, 'missing_snapshots', missing)

        # calc and store snapshots_success prop
        snapshots_success = (err=='' and
                            not timeout_hit and
                            len(missing)==0)
        db.set_prop_value(script, 'snapshots_success', snapshots_success)

        # calc and store snapshots_diagnostic prop
        snapshots_diagnostic = ''
        if not snapshots_success:
            if timeout_hit:
                err = ('Timeout hit. Remember in this case it is posible not all stderr captured.\n' +
                       err)
            if len(missing):
                missing = [ os.path.basename(s) for s in missing ]
                err += '\nNot all snapshots captured - missing snapshots:\n'
                err += '\n'.join(missing)
            snapshots_diagnostic = err
            print 'err:', err
        db.set_prop_value(script, 'snapshots_diagnostic', snapshots_diagnostic)


    # update history
    text = '\n'.join(known_scripts)
    db.history_add('update_snapshots', text)

    dbm.db_save(db, filename_persist)
    return known_scripts, unknowns

def _update_testrun(db, candidates_w_props, snapshots_dir):
    """
    the propdict for each candidate must have been tested for keys in testrun
    """

    known_scripts, unknowns = db.entities(candidates=candidates_w_props)
    ignored = set()

    for script in known_scripts:
        fname = db.fname_from_canonical(script)
        propdict = scanprops_from_fname(fname)

        if propdict != db.get_groupdict(script, 'scan'):
            # potential changes in script after snapshots done, ignore
            ignored.add(script)
            continue
        d = copy.deepcopy(candidates_w_props[script])
        d['testrun_md5'] = propdict['md5_at_testinfo']
        db.set_groupdict(script, 'testrun', d)

    checked_in = set([k for k in known_scripts if k not in ignored])
    return checked_in, ignored, unknowns


def update_testrun__pass(db, filename_persist, candidates,
                         snapshots_dir, snapshots_reference_dir=None):
    """
    snapshots_reference_dir : dir to move snapshots; if None no move
    """
    
    if snapshots_reference_dir:
        if not os.path.isdir(snapshots_dir):
            raise ValueError("snapshot dir not found or not a dir:%s"%snapshots_dir)
        if not os.path.exists(snapshots_reference_dir):
            os.makedirs(snapshots_reference_dir)

    pass_dict = {
        'testrun_success': 'pass',
        'testrun_diagnostic': '',
        }

    candidates_w_props = dict([(k, pass_dict) for k in candidates])
    checked_in, ignored, unknown = _update_testrun(db, candidates_w_props,
                                                   snapshots_dir)

    move_failed = set()
    if snapshots_reference_dir:
        # move snapshots to reference dir 
        for script in checked_in:
            snapshots = db.get_prop_value(script, 'expected_snapshots')
            moved, cant_move = doers.move_files(snapshots, snapshots_dir,
                                                snapshots_reference_dir)
            if cant_move:
                db.del_groupdict(script, 'testrun')
                move_failed.add(script)

    checked_in -= move_failed 
    return checked_in, unknown, move_failed

# >>> some useful selectors

def fn_allow_all(propdict):
    return True

def fn_allow_testinfo_valid(propdict):
    return ('testinfo_diagnostic' in propdict and
            propdict['testinfo_diagnostic']=='')

def fn_allow_testinfo_missing(propdict):
    return 'testinfo' not in propdict

def fn_allow_testinfo_invalid(propdict):
    return ('testinfo_diagnostic' in propdict and
            propdict['testinfo_diagnostic']!='')

def fn_allow_snapshots_success(propdict):
    return 'snapshots_success' in propdict and propdict['snapshots_success']

def fn_allow_snapshots_failure(propdict):
    return 'snapshots_success' in propdict and not propdict['snapshots_success']

def fn_allow_IOerror(propdict):
    return 'IOerror' in propdict and propdict['IOerror']
    
def fn_allow_testrun_pass(propdict):
    return 'testrun_success' in propdict and propdict['testrun_success']=='pass'

def get_scripts(db, selector, candidates=None, testbed=None):
    was_unknown = (selector == 'unknown')
    if was_unknown:
        selector = 'all'
        
    func_name = "fn_allow_%s"%selector
    func = getattr(sys.modules[text_props_simple.__module__], func_name)
    selected, unknown = db.entities(fn_allow=func,
                                   candidates=candidates,
                                   testbed=testbed)

    if was_unknown:
        selected = unknown
        unknown = set()

    return selected, unknown

# >>> high level reports

def section(db, selector, candidates=None, verbose=None, testbed=None):
    headers = {
        # selector: header
        'testinfo_valid': "Scripts that have testinfo and it is valid",
        'testinfo_invalid': "Scripts that have testinfo and it is not valid",
        'testinfo_missing': "Scripts that don't have testinfo",
        'all': "All scripts",
        'snapshots_success': "Scripts that have taken snapshots succesfuly",
        'snapshots_failure': "Scripts that atempted to take snapshots but failed",
        'unknown': "Scripts not known to the db",
        'IOerror': "Scripts that can't be readed",
        'testrun_pass': "Scripts showing correct behavior and snapshots reflect that",
        }
    scripts, unknown = get_scripts(db, selector, candidates, testbed)
    scripts = sorted(scripts)

    if candidates is None:
        num_candidates = db.num_entities(testbed)
    else:
        num_candidates = len(candidates)    
    text_parts = []
    
    if verbose:
        prefix = ': '
    else:
        prefix = ''
    header_tail = "(%d / %d)"%(len(scripts), num_candidates)
    text_parts.append("%s%s %s"%(prefix, headers[selector], header_tail))
    if verbose:# and len(scripts):
        text_parts.append('\n')
        text_parts.extend(scripts)
    text = '\n'.join(text_parts)
    return text

def rpt(db, selectors, candidates=None, verbose=True, testbed=None):
    text_parts = ['\n']
    for selection in selectors:
        text_parts.append(section(db, selection, candidates, verbose, testbed))
    text = '\n'.join(text_parts)
    return text
        
def rpt_detail_diagnostics(db, selector, candidates=None, testbed=None):
    prop = {'snapshots_failure': 'snapshots_diagnostic',
            'testinfo_invalid': 'testinfo_diagnostic'}
    if selector not in prop:
        return '\nNo detailed report available for selector = ' + selector 
    scripts, unknown = get_scripts(db, selector, candidates, testbed)
    scripts = sorted(scripts)
    text_parts = ['\n\nDetails %s errors'%selector]
    for entity in scripts:
        text_parts.append("\n%s\n"%entity)
        text_parts.append(db.get_prop_value(entity, prop[selector], testbed=testbed))
        text_parts.append('-'*78)
    text = '\n'.join(text_parts)
    return text
