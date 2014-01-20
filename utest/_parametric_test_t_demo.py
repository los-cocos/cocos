from __future__ import division, print_function, unicode_literals

# example running test with diferent parameters.
# here we use py.test to run the test
# references:
# http://tetamap.wordpress.com/2009/05/13/parametrizing-python-tests-generalized/
# code here is a modification of test_parametrize3.py in that page
##run with
##py.test -v _parametric_test_t_demo.py
##(you may need to put pythonxx\scripts in your path)

def pytest_generate_tests(metafunc):
    param_names = ['duration1', 'duration2']
    values = [  (0.0, 0.0),
                (0.0, 3.0),
                (3.0, 0.0),
                (3.0, 3.0),
                (3.0, 5.0),
                (5.0, 3.0)
                ]
    scenarios = {}
    for v in values:
        name = ' '.join(['%s'%e for e in v])
        scenarios[name] = dict(zip(param_names, v))
    for k in scenarios:
        metafunc.addcall(id=k, funcargs=scenarios[k])

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


### ? can we have a non-parametrized test in same file ?
##class TestSampleNoParameters:
##    def test_demo(self):
##        assert 1==1
### ? not this way: the test are called with params, so a 'unexpected argument'
### triggers
        
