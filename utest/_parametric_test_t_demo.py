from __future__ import division, print_function, unicode_literals

import pytest
# example running test with diferent parameters, for pytest >= 4.0
# reference: https://docs.pytest.org/en/5.1.2/parametrize.html
#
# run with
# py.test -v _parametric_test_t_demo.py
# (you may need to put pythonxx\scripts in your path)
#
# example line from the output:
# _parametric_test_t_demo.py::TestSampleWithParameters::test2_demo[d1_gt_5] PASSED [ 63%]
# notice how the 'd1_gt_5' comes from the params in the call to parametrize
#
# Theres many ways to build the params for parametrize, this seems sensible 

def params_for_TestSampleWithParameters():
    param_names = ['duration1', 'duration2']
    cases = [ ((0.0, 0.0), "d1_eq_d2_eq_0"),
                   ((0.0, 3.0),  "d1_eq_0_d2_gt_0"),
                   ((3.0, 0.0),  "d1_lt_4_d2_eq_0"),
                   ((3.0, 3.0),  "d1_eq_d2_lt_4"),
                   ((3.0, 5.0),  "d1_lt_4_d2_gt_4"),
                   ((5.0, 3.0),  "d1_gt_5"),
                ]
    params = [e[0] for e in cases]
    sufixes_parametrized_tests = [e[1] for e in cases] 
    # return tuple must match pytest.mark.parametrize signature; for pytest 5.1.2
    # it is Metafunc.parametrize(argnames, argvalues, indirect=False, ids=None, scope=None)
    return (param_names, params, False,  sufixes_parametrized_tests)
    
# (argnames, argvalues, indirect=False, ids=None, scope=None)
@pytest.mark.parametrize(*params_for_TestSampleWithParameters())
class TestSampleWithParameters:

    def test_demo(self, duration1, duration2):
        assert isinstance(duration1, float)

    def test2_demo(self, duration1, duration2):
        assert isinstance(duration2, float)

    def test3_demo(self, duration1, duration2):
        # can we skip test on certain params conditions ?
        if duration1>4.0:
            return
        assert duration1>=0.0
        # yes, the test listed as PASS in the case with duration1 == 5.0


# ? can we have a non-parametrized test in same file ?
class TestSampleNoParameters:
    def test_demo(self):
        assert 1==1
# Yes!
        
