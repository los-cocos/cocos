from __future__ import division, print_function, unicode_literals

import pytest
import helpers as hl

def test_testinfo_payload__matchs():
    testinfo = "1234"
    text = 'asdasd \ntestinfo= "' + testinfo + '"   \nZZZ'
    assert hl.testinfo_payload(text) == testinfo

def test_testinfo_payload__no_matchs():
    text = 'asdasd \ntestinfo= ' + '   \nZZZ'
    assert hl.testinfo_payload(text)==None

    
