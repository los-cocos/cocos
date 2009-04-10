
__all__ = ['Interpreter']

try:
    import readline
    has_readline = True
except:
    has_readline = False
import sys

from code import InteractiveInterpreter
from pyglet.event import EventDispatcher

from cocos.utils import FileIn, FileOut

from history import History
from completer import Completer


class Interpreter(InteractiveInterpreter, EventDispatcher):
    def __init__(self, ns_locals=None, ns_globals=None,
                 stdin=None, stdout=None, stderr=None,
                 history_file=None, history_size=100,
                 history_persistent=False):

        # redirect input and output
        if stdin is None:
            stdin = sys.stdin
        if stdout is None:
            stdout = sys.stdout
        if stderr is None:
            stderr = sys.stderr
        self.stdin = FileIn(stdin, sys.stdin.fileno())
        self.stdout = FileOut(stdout, sys.stdout.fileno())
        self.stderr = FileOut(stderr, sys.stderr.fileno())

        # set up interpreter engine
        if ns_locals is None:
            ns_locals = {}
        if ns_globals is None:
            ns_globals = {}

        self.history = self.init_history(history_file, history_size,
                                         history_persistent)
        namespace = ns_globals.copy()
        namespace.update(ns_locals)
        self.completer = self.init_completer(namespace)
        super(Interpreter, self).__init__(locals=namespace)

    def init_history(self, filename, size, persistent):
        if has_readline:
            from history import ReadlineHistory
            history = ReadlineHistory(filename, size, persistent)
        else:
            history = History(filename, size, persistent)
        return history

    def init_completer(self, namespace=None):
        if has_readline:
            from completer import ReadlineCompleter
            completer = ReadlineCompleter(namespace)
        else:
            completer = Completer(namespace)
        return completer

    def execute(self, command):
        more = False
        self.toggle_env()
        try:
            more = self.runsource(command)
            self.history.append(command)
        except Exception, e:
            self.toggle_env()
            print e
        else:
            self.toggle_env()
        return more

    def toggle_env(self):
        self.stdin, sys.stdin = sys.stdin, self.stdin
        self.stdout, sys.stdout = sys.stdout, self.stdout
        self.stderr, sys.stderr = sys.stderr, self.stderr

    #################
    # Common Events
    #################
    def on_exit(self):
        self.history.persist()

    #################
    # Command Events
    #################
    def on_command(self, command):
        self.execute(command)
        self.dispatch_event('on_command_done')

    def on_completion(self, command):
        if not command.strip():
            return
        completed, possibilities = self.completer.complete(command)
        output = []
        if len(possibilities) > 1:
            slice = command
            output.append('\n')
            for symbol in possibilities:
                output.append(symbol + '\n')
        self.dispatch_event('on_completion_done', completed or slice, ''.join(output))

    def on_history_prev(self, command):
        item = self.history.previous()
        self.dispatch_event('on_history_result', item)

    def on_history_next(self, command):
        item = self.history.next()
        self.dispatch_event('on_history_result', item)

    def update_namespace(self, ns_locals=None, ns_globals=None):
        namespace = self.completer.namespace
        if ns_globals is not None:
            namespace.update(ns_globals)
        if ns_locals is not None:
            namespace.update(ns_locals)
        self.completer.namespace = namespace

Interpreter.register_event_type('on_command_done')
Interpreter.register_event_type('on_completion_done')
Interpreter.register_event_type('on_history_result')
