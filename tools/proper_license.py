#!/usr/bin/python
# $Id:$

'''report files which not begin with the harcoded license 

Usage:
    proper_license.py file.py file.py dir/ dir/ ...
'''

import optparse
import os
import sys


old_license = """# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
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


def have_proper_license(filename):
    '''Open a Python source file and check if exactly begins with the
    text provided in the global license_
    Side effect: if the global report_no_proper is True will print the filename
    '''
    global license_
    f = open(filename, 'rb')
    text = f.read()
    res = text.startswith(license_)
    f.close()
    if report_no_proper and not res:
        print filename
    return res
    
if __name__ == '__main__':
    license_ = old_license
    #license_ = new_license
    report_no_proper = True
    
    op = optparse.OptionParser()
    op.add_option('--exclude', action='append', default=[])
    options, args = op.parse_args()
    
    if len(args) < 1:
        print >> sys.stderr, __doc__
        sys.exit(0)

    for path in args:
        if os.path.isdir(path):
            for root, dirnames, filenames in os.walk(path):
                for dirname in dirnames:
                    if dirname in options.exclude:
                        dirnames.remove(dirname)
                for filename in filenames:
                    if (filename.endswith('.py') and 
                        filename not in options.exclude):
                        have_proper_license(os.path.join(root, filename))
        else:
            have_proper_license(path)
