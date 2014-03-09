from __future__ import division, print_function, unicode_literals
import six

if six.PY3:
    def asciibytes(s):
        return bytes(s, "ASCII")
else:
    def asciibytes(s):
        if type(s) != bytes:
            s = s.encode("ASCII")
        return s
