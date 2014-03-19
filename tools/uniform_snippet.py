#!/usr/bin/python
# $Id:$

"""checks that certain code snipets are the same across the samples and test
directories.

This is a release helper.

Usage:
    uniform_snippet.py [<task_selection>]

Where <task_selection> one of:
    --report
        list files using a different variation of reference snipet

    --report-verbose
        as report, but also prints the matching block

    --report-bigs
        list only files with a matching block bigger than the reference block

    --report-using
        list files using the exact reference snipet

    --fix
        any non compliant file is modified by replacing the matching block
        with the reference block
        console output is the list of modified files

Default option is --report

When using --report or --report-verbose the script return value will be
0 (success) if all files are compliant
nonzero otherwise

Release workflow:
    1. run with report-bigs
    for each file reported, analize if it should be the new reference snipet
    or it is a special case.
    If a special case, rename the class / funcion, else change the reference
    snipet
    2. run with report (and save the results)
    If no file is reported, the job is done
    If they are files reported
        run with report-verbose
        analize the results, renaming the non compliant classes / functions
        when it is a special case
    3. run with fix
    to replace the remaining non compliant snipets with the referece snipet
    4. test all the scripts changed in the process.
"""
from __future__ import division, print_function, unicode_literals
import six

import os
import sys

##def chain(*iterables):
##    # chain('ABC', 'DEF') --> A B C D E F
##    for it in iterables:
##        for element in it:
##            yield element

class SnipetCompliance(object):
    @classmethod
    def set_target(cls, reference_text, start_mark=None):
        reference_text = reference_text.rstrip()
        cls.reference_lines = reference_text.split('\n')[1:]
        infered_start_mark = cls.reference_lines[0].strip().replace(' ', '')
        if start_mark is None:
            cls.begin_string = infered_start_mark
        else:
            assert infered_start_mark.startswith(start_mark)
            cls.begin_string = start_mark

    def __init__(self, fname, text):
        self.fname = fname
        self.text = text
        self.prepare()

    def prepare(self):
        self.lines = self.text.split('\n')
        self.iter_enumerated_lines = enumerate(self.lines)
        self.compliant = None
        self.is_present = None

    def is_compliant(self):
        if self.compliant is not None:
            return self.compliant
        self.start_line = get_start_line(self.iter_enumerated_lines, self.begin_string)
        self.is_present = self.start_line is not None
        self.endplus_line = None
        if not self.is_present:
            self.compliant = True
        else:
            self.endplus_line = get_endplus_line(self.iter_enumerated_lines)

            # a bit strong (whitespace matters), but lets go with simple code
            self.compliant = (self.reference_lines ==
                              self.lines[self.start_line : self.endplus_line])
        return self.compliant

    def matched(self):
        if self.is_present is None:
            self.is_compliant()
##        print('self.is_present:', self.is_present)
##        print('self.compliant:', self.compliant)
        if self.is_present:
##            print('start_line:', self.start_line)
##            print('endplus_line:', self.endplus_line)
            s = '\n'.join(self.lines[self.start_line: self.endplus_line])
        else:
            s = ''
        return s

    def bigger(self):
        return (self.endplus_line - self.start_line) > len(self.reference_lines)

    def enforce_compliance(self):
        if self.is_compliant():
            return
        # replace matched code by the reference code
        self.lines[self.start_line : self.endplus_line] = self.reference_lines
        self.text = '\n'.join(self.lines)
        
        self.prepare()
        self.is_compliant()
        assert self.compliant
        #self.compliant = True


reference = """
class BackgroundLayer(cocos.layer.Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        glColor4ub(255, 255, 255, 255)
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()
"""


def get_start_line(iter_enumerated_lines, target):
    """-> line number where the target string matches the start of line

    Consumes the iterator until a line with a match is found or untilt the
    iterator is exhausted.
    
    Returns the line number where the match was found or None if no match.
    After the return, a call to the iterator 'next' method would yield
    the (lineno, line) for the line following the matching line.
    
    It discards whitespace in the lines provided by the iterator before
    comparison.
    """
    try:
        while 1:
            lineno, line = six.next(iter_enumerated_lines)
            line = line.strip()
            line = line.replace(' ', '')
            if line.startswith(target):
                start_line = lineno
                break
    except StopIteration:
        # target not present
        start_line = None
    return start_line

def get_endplus_line(iter_enumerated_lines):
    """
    Advances the iterator until a nonblank line with zero indentation is found.
    Returns the line number of the last non whitespace line with indentation
    greater than zero.
    """
    # seek end of object code as the next line with zero indentation
    # will broke with comments at 0 indent amidst the object code
    # class / func definition should be in lines[start_line : endplus_line]
    # trailing whitespace lines are not included
    last_no_blank = None
    while 1:
        try:
            lineno, line = six.next(iter_enumerated_lines)
        except StopIteration:
            # EOF
            break
        if len(line)>0 and not line[0].isspace():
            # a line with indentation zero, the object code should
            # have ended at most one line above
            if last_no_blank is None:
                last_no_blank = lineno-1
            break
        if len(line)>0 and not line.isspace():
            last_no_blank = lineno
    return last_no_blank + 1

##def save_modified(file_):
##    for line in itertools.chain(
##                    lines[start_line: start_line+len(reference_lines)],
##                    reference_lines,
##                    ['\n',],
##                    lines[endplus_line: -1]):
##        file_.write(line)

if __name__ == '__main__':
    task_to_flags = {
        #key = (report_compliant, report_only_big, report_show_matching_block, fix)
        '--report': (False, False, False, False),
        '--report-verbose': (False, False, True, False),
        '--report-bigs': (False, True, True, False),
        '--report-using': (True, False, False, False),
        '--fix': (False, False, False, True)
        }

    if len(sys.argv) == 1:
        task = '--report'
    elif len(sys.argv)==2 and sys.argv[1] in task_to_flags:
        task = sys.argv[1]
    else:
        print(__doc__, sys.stderr)
        sys.exit(0)

    (report_compliant, report_only_big,
             report_show_matching_block, fix) = task_to_flags[task]

    # Asumes script runs from trunk/tools
    # Only scripts strictly in the test directory are considered.
    dir_path = '../test'

    SnipetCompliance.set_target(reference, 'classBackgroundLayer(')

    all_compliant = True
    for short_name in os.listdir(dir_path):
        if short_name.endswith('.py'):
            # use sep = '/' even in windows to better cooperation with autotest
            fname = '/'.join([dir_path, short_name])
            f = open(fname, 'rb')
            text = f.read()
            f.close()
            worker = SnipetCompliance(fname, text)
            file_compliant = worker.is_compliant()
            all_compliant = all_compliant and file_compliant
            if report_compliant == file_compliant:
                if file_compliant and worker.is_present:
                    # strip initial '../' for better colaboration with autotest
                    print(fname[3:])
                else:
                    if (not report_only_big or
                        (report_only_big and worker.bigger())):
                        # strip initial '../' for better colaboration with autotest
                        print(fname[3:])
                        if report_show_matching_block:
                            print('\n>>>')
                            print('matched:')
                            print(worker.matched())
                            print('<<<\n')

            if fix and not file_compliant:
                worker.enforce_compliance()
                f = open(fname, 'wb')
                f.write(worker.text)
                f.close()
    cmd_result = not all_compliant and task in ['--report', '--report-verbose']
    sys.exit(cmd_result)

