import rlcompleter

from completer import Completer


class ReadlineCompleter(Completer):
    def __init__(self, namespace=None):
        super(ReadlineCompleter, self).__init__(namespace)
        self._completer = rlcompleter.Completer(namespace)

    def _get_completion(self, char, index):
        return self._completer.complete(char, index)

    @apply
    def namespace():
        def fget(self):
            return self._completer.namespace
        def fset(self, value):
            self._completer.namespace = value
        return property(fget, fset)


