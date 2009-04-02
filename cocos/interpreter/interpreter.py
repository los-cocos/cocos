
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
                 history_file=None, history_size=100):

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

        self.history = self.init_history(history_file, history_size)
        self.completer = self.init_completer(ns_locals)
        super(Interpreter, self).__init__(locals=ns_locals)

    def init_history(self, filename, size):
        if has_readline:
            from history import ReadlineHistory
            history = ReadlineHistory(filename, size)
        else:
            history = History(filename, size)
        return history

    def init_completer(self, namespace=None):
        if has_readline:
            from completer import ReadlineCompleter
            completer = ReadlineCompleter(namespace)
        else:
            completer = Completer(namespace)
        return completer

    def execute(self, command):
        self.toggle_env()
        try:
            more = self.runsource(command)
            self.history.append(command)
        except Exception, e:
            print e
        self.toggle_env()
        return more

    def toggle_env(self):
        self.stdin, sys.stdin = sys.stdin, self.stdin
        self.stdout, sys.stdout = sys.stdout, self.stdout
        self.stderr, sys.stderr = sys.stderr, self.stderr

    def on_command(self, command):
        self.execute(command)
        self.stdout.dispatch_event('on_command_done')

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
        self.stdout.dispatch_event('on_completed', completed or slice, ''.join(output))

    def on_history_prev(self, command):
        item = self.history.previous()
        self.stdout.dispatch_event('on_set_command', item)

    def on_history_next(self, command):
        item = self.history.next()
        self.stdout.dispatch_event('on_set_command', item)

    def on_update_completer(self, ns_locals):
        self.completer.namespace = ns_locals

    def on_exit(self):
        self.history.save()

Interpreter.register_event_type('on_command')
Interpreter.register_event_type('on_completion')
Interpreter.register_event_type('on_history_prev')
Interpreter.register_event_type('on_history_next')
Interpreter.register_event_type('on_update_completer')
Interpreter.register_event_type('on_exit')
