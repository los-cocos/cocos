import os.path
import re


class Completer(object):
    def __init__(self, namespace=None):
        self._namespace = namespace
        self._completer = None
        self.complete_sep = re.compile('[\s\{\}\[\]\(\)]')

    def complete(self, line):
        split_line = self.complete_sep.split(line)
        possibilities = []
        i = 0
        c = self._get_completion(split_line[-1], i)
        while c:
            possibilities.append(c)
            i = i + 1
            c = self._get_completion(split_line[-1], i)
        if possibilities:
            common_prefix = os.path.commonprefix(possibilities)
            completed = line[:-len(split_line[-1])] + common_prefix
        else:
            completed = line
        return completed, possibilities

    def _get_completion(self, char, index):
        return ''

    @apply
    def namespace():
        def fget(self):
            return self._namespace
        def fset(self, value):
            self._namespace = value
        return property(fget, fset)
