"""tests tools\\uniform_snippet.py , use py.test to run"""
from __future__ import division, print_function, unicode_literals
import six

# make the test find the script in tools directory
import sys, os
tools_path = '../tools'
tools_abspath = os.path.abspath(tools_path)
sys.path.insert(0, tools_abspath) 

from uniform_snippet import  get_start_line, get_endplus_line, SnipetCompliance

#testing get_start_line
# better name would be  get_first_match ?
#Note: target must not contain whitespace, else fails

def test_start_1st_line_match():
    target = 'classBackgroundLayer('
    should_match = 'class BackgroundLayer(cocos.layer.Layer)'
    filling = '\n'.join([
        'this is a line',
        'this is another'
        ])
    text = should_match + '\n' + filling
    lines = text.split('\n')
    it = enumerate(lines)

    start_line = get_start_line(it, target)
    assert start_line == 0
    assert six.next(it) == (1, lines[1])


def test_start_last_line_match():
    target = 'classBackgroundLayer('
    should_match = 'class BackgroundLayer('
    filling = '\n'.join([
        'this is a line',
        'this is another'
        ])
    text = filling + '\n' + should_match
    lines = text.split('\n')
    it = enumerate(lines)

    start_line = get_start_line(it, target)
    assert start_line == 2
    # here next should raise StoptIteration
    StopIteration_raised = False
    try:
        six.next(it)
    except StopIteration:
        StopIteration_raised = True
    assert StopIteration_raised

def test_start_inner_line_match():
    target = 'classBackgroundLayer('
    should_match = 'class BackgroundLayer(cocos.layer.Layer)'
    filling = '\n'.join([
        'this is a line',
        'this is another'
        ])
    text = 'A fine first line.\n' + should_match + '\n' + filling
    lines = text.split('\n')
    it = enumerate(lines)

    start_line = get_start_line(it, target)
    assert start_line == 1
    assert six.next(it) == (2, lines[2])

def test_start_no_match():
    target = 'classBackgroundLayer('
    filling = '\n'.join([
        'this is a line',
        'this is another'
        ])
    text = filling
    lines = text.split('\n')
    it = enumerate(lines)

    start_line = get_start_line(it, target)
    assert start_line is None
    # here next should raise StoptIteration
    StopIteration_raised = False
    try:
        six.next(it)
    except StopIteration:
        StopIteration_raised = True
    assert StopIteration_raised

# start tests for get_endplus_line
# better name can be : seek_end_of_indented_block
def test_endplus_with_trailing_blank_lines():
    text = '\n'.join([
            '     An indented line.',
            '\n',
            '\tLast non whitespace indented line.',
            '\n',
            '\n \t \r',
            '\n',
            'First non whitspace non indented line'
            ])
    lines = text.split('\n')
    it = enumerate(lines)

    endplus_line = get_endplus_line(it)
    assert lines[endplus_line-1] == '\tLast non whitespace indented line.'

def test_endplus_with_no_trailing_blank_lines():
    text = '\n'.join([
            '     An indented line.',
            '\n',
            '\tLast non whitespace indented line.',
            'First non whitspace non indented line'
            ])
    lines = text.split('\n')
    it = enumerate(lines)

    endplus_line = get_endplus_line(it)
    assert lines[endplus_line-1] == '\tLast non whitespace indented line.'


def test_endplus_hitting_first_line():
    text = '\n'.join([
            'First non whitespace non indented line',
            '     An indented line.',
            '\n',
            '\tLast non whitespace indented line.',
            ])
    lines = text.split('\n')
    it = enumerate(lines)

    endplus_line = get_endplus_line(it)
    assert lines[endplus_line] == 'First non whitespace non indented line'

def test_endplus_hitting_EOF():
    text = '\n'.join([
            '     An indented line.',
            '\n',
            '\tLast non whitespace indented line.'
            ])
    lines = text.split('\n')
    it = enumerate(lines)

    endplus_line = get_endplus_line(it)
    assert lines[endplus_line-1] == '\tLast non whitespace indented line.'

## if desided to run withou py.test              
##test_start_1st_line_match()
##test_start_last_line_match()
##test_start_inner_line_match()
##test_start_no_match()
##test_endplus_with_trailing_blank_lines()
##test_endplus_with_no_trailing_blank_lines()
##test_endplus_hitting_EOF()
##test_endplus_hitting_first_line()

# aqui habria que empezar a hacer tests para la clase

##reference = """
##class BackgroundLayer(cocos.layer.Layer):
##    def __init__(self):
##        super(BackgroundLayer, self).__init__()
##        self.img = pyglet.resource.image('background_image.png')
##
##    def draw( self ):
##        glColor4ub(255, 255, 255, 255)
##        glPushMatrix()
##        self.transform()
##        self.img.blit(0,0)
##        glPopMatrix()
##"""
##
##text_0 = """
###one up
##
##class BackgroundLayer(cocos.layer.Layer):
##    def __init__(self):
##        super(BackgroundLayer, self).__init__()
##        self.img = pyglet.resource.image('background_image.png')
##
##    def draw( self ):
##        glColor4ub(255, 255, 255, 255)
##        glPushMatrix()
##        self.transform()
##        self.img.blit(0,0)
##        glPopMatrix()
##
###one down
##"""
##
##def test_midle_text_compliant():
##    line_0 = '#line 0'
##    line_last = '#line last'
##    text_0 = line_0 + '\n' + reference + line_last
##    print(text_0)
##    SnipetCompliance.set_target(reference, 'classBackgroundLayer(')
##    worker = SnipetCompliance('', text_0)
##    worker.is_compliant()
##    print('\n>>>')
##    print('matched:')
##    print(worker.matched())
##    print('<<<\n')
##
##    worker.enforce_compliance()
##    print '\n>>>'
##    print 'matched:'
##    print worker.matched()
##    print '<<<\n'
##
##    print 'fixed text:'
##    print worker.text
##
##
##def test_midle_text_compliant():
##    line_0 = '#line 0'
##    line_last = '#line last'
##    text_0 = line_0 + '\n' + reference + line_last
##    print(text_0)
##    SnipetCompliance.set_target(reference, 'classBackgroundLayer(')
##    worker = SnipetCompliance('', text_0)
##    worker.is_compliant()
##    assert worker.compliant
##    worker.enforce_compliance()
##    assert text_0 == worker.text
####    print('\n>>>')
####    print('matched:')
####    print(worker.matched())
####    print('<<<\n')
####
####    worker.enforce_compliance()
####    print('\n>>>')
####    print('matched:')
####    print(worker.matched())
####    print('<<<\n')
####
####    print('fixed text:')
####    print(worker.text)
##    
##def test_trailing_text_compliant():
##    line_0 = '#line 0'
##    text_0 = line_0 + '\n' + reference
##    print(text_0)
##    SnipetCompliance.set_target(reference, 'classBackgroundLayer(')
##    worker = SnipetCompliance('', text_0)
##    worker.is_compliant()
##    assert text_0 == worker.text
##    assert worker.compliant
####    print('\n>>>')
####    print('matched:')
####    print(worker.matched())
####    print('<<<\n')
####
####    worker.enforce_compliance()
####    print('\n>>>')
####    print('matched:')
####    print(worker.matched())
####    print('<<<\n')
####
####    print('fixed text:')
####    print(worker.text)
##test_midle_text_compliant
##test_trailing_text_compliant()
