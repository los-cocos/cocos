from __future__ import division, print_function, unicode_literals

#py.test script must be in the path
#you must set cocos_utest to 1 in the environment before running

import sys
import os

def usage():
    cmd = os.path.basename(sys.argv[0])
    print("""
Usage:
    %s filename
        filename: points to a file which list, one by line,
        the test names we want to run
Action:
    same as
    py.test -v testname1 testname2 ...
    where tesnamei is quoted to hide spaces

Notes:
    py.test should be in the path
    you must set cocos_utest to 1 in the environment before running
    tests names must include the .py ending ( ex: test_actions.py )
    test names can have embedded spaces ( ex: test xyz.py)
    test names are blank-stripped
    blank lines are ignored
    warn: big lists can hit the max command line lenght:
      win2000 2047
      winXP   8191
    """%cmd)

def get_list(fname):
    f = open(fname, 'rb')
    text = f.read()
    f.close()
    text.replace('\r', '')
    lines = text.split('\n')
    lines = [ e.strip() for e in lines]
    if os.sep=='\\':
        quote = '"'
    else:
        quote = "'"
    lines = [ (quote + e + quote) for e in lines if len(e)]     
    return lines

def proceed(fname):
##    os.environ['cocos_utest'] = '1' #? not propagated
    if os.environ.get('cocos_utest',None) is None:
        print('err: you should SET cocos_utest to 1 in the environment')
        return
    tests = get_list(fname)
    os.system('set cocos_utest=1') 
    cmd = 'py.test -v ' + ' '.join(tests)
    print(cmd)
    os.system(cmd) 

if len(sys.argv)!=2:
    usage()
else:
    proceed(sys.argv[1])
