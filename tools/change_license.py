#!/usr/bin/python
# $Id:$

"""script to work licence header - see usage or use --help 

For the last cocos releases we need to run over ..\cocos  and skeleton
Be sure to check the hardcoded old_license, new_license, exclude are
the one intended.
use svn status to confirm what changed.
"""
from __future__ import division, print_function, unicode_literals

import optparse
import os
import sys

old_license =  """# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2014  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------"""


new_license = """# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------"""

change_files = False
report_match = False
reported = []
target_license = None

headers = {
    'list-matching-new': 'Files with the new license:',
    'list-non-matching-new': 'Files without the new license:',
    'list-matching-old': 'Files with the old license:',
    'list-non-matching-old': 'Files not matching the old license',
    'change': 'Files changed:'}

exclude = set([
    'pygame',
    'SDL',
    'euclid'
    ])

# no proper error handling. If in trouble, svn revert , solve the problem,
# try again.
def process_file(filename):
    '''Open a Python source file and check if exactly begins with the
    text provided in the global old_license; if yes, replace that text with
    the one in the global new_license.
    Side effect: if the global report_not_changed is True will print the filename
    if the file dont begins with the old_license text    
    '''
    global target_license, new_license, change_files, report_match, reported
    f = open(filename, 'rU')
    text = f.read()
    f.close()
    match = text.startswith(target_license)
    if change_files and match:
        text = new_license + text[len(target_license):]
        f = open(filename, 'w')
        f.write(text)
        f.close()
    if report_match == match:
        reported.append(filename)
    
if __name__ == '__main__':
    usage = """
    %prog [options] path1 path2 ...

    With MODE one of 'list-matching-new', 'list-non-matching-new',
    'list-matching-old', 'list-non-matching-old' reports the files matching
    (or not matching) the new or old license.

    With MODE=change files matching the old license are changed to the new one.

    Default MODE is 'list-non-matching-old', meaning the files that don't match
    the old license.
    """
    op = optparse.OptionParser(usage = usage)
    op.add_option('--mode', dest='mode', default='list-non-matching-old',
                  choices=['list-matching-new', 'list-non-matching-new',
                            'list-matching-old', 'list-non-matching-old',
                            'change'],
                  )
    options, args = op.parse_args()

    if len(args) < 1:
        op.print_usage()
        sys.exit(0)

    mode = options.mode
    print('mode:', mode)

    assert mode in headers

    print(headers[mode])
    change_files = (mode == 'change')
    if change_files:
        mode = 'list-matching-old'
    if mode.endswith('old'):
        target_license = old_license
    else:
        target_license = new_license
    report_match = not ('non' in mode)

    for path in args:
        print('args:', args)
        if os.path.isdir(path):
            for root, dirnames, filenames in os.walk(path):
                for dirname in dirnames:
                    if dirname in exclude:
                        dirnames.remove(dirname)
                for filename in filenames:
                    if (filename.endswith('.py') and 
                        filename not in exclude):
                        try:
                            process_file(os.path.join(root, filename))
                        except Exception as ex:
                            print("Exception while processing %s" % os.path.join(root, filename))
                            print(ex)
                            
        else:
            if (path.endswith('.py') and 
                path not in exclude):
                process_file(path)

    for name in reported:
        print(name)
