
Running:

tests with filenames like test_p_* depends on py.test
py.test can run tests written for unittest.
latest py.test version used : pytest 2.1.0

For most tests, you must set cocos_utest=1 in the environment before running.
You should have py.test in the executable search path

Running one test:
 cd utest
 py.test [flags] test_file.py

Running all tests:
 cd utest
 py.test [flags]

Running a subset of all tests:
Use runner1.py with a custom list (see details in runner1.py)
 cd utest
 runner1.py my_list.txt
Or look at py.test docs


Coding:

Mockups, tests and test runners must be kept very simple, both to reduce the
bug count and to encourage people to write unit tests.

In unit tests, whenever possible you will want to replace pyglet with a
lightweight mockup for fast setUp.

Ideally we will have two or three pyglet mockups, providing increasing
functionality.

You should try to code for the most simple mockup that will support your test.

The readme in each mockup directory should describe which functionality supports,
and guidelines about what to not add at this mockup.
At the time we have only one pyglet mockup, found at
utest\pyglet_mockup1
See the readme in the mockup directory for capabilities.
See any test_p_ba_* test for examples using pyglet_mockup1.

It is important to keep director.py dependencies low: almost anything in cocos
needs to instantiate a director, so increasing the dependencies will need more
complex setUp or mockups, and more running time.
