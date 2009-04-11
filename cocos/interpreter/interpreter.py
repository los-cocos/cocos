# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2009 cocos2d
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''A base python interpreter for embedding into a layer

Interpreter
===========

TBD

'''

__docformat__ = 'restructuredtext'
__all__ = ['Interpreter']

try:
    import readline
    has_readline = True
except:
    has_readline = False
finally:
    del readline
import sys

from code import InteractiveInterpreter
from pyglet.event import EventDispatcher

from cocos.utils import FileIn, FileOut

from history import History
from completer import Completer


def init_history(filename, size, persistent):
    if has_readline:
        from history import ReadlineHistory
        history = ReadlineHistory(filename, size, persistent)
    else:
        history = History(filename, size, persistent)
    return history

def init_completer(namespace=None):
    if has_readline:
        from completer import ReadlineCompleter
        completer = ReadlineCompleter(namespace)
    else:
        completer = Completer(namespace)
    return completer


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

        self.history = init_history(history_file, history_size,
                                    history_persistent)

        namespace = ns_globals.copy()
        namespace.update(ns_locals)
        self.completer = init_completer(namespace)

        super(Interpreter, self).__init__(locals=namespace)

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
            output.append('\n')
            for symbol in possibilities:
                output.append(symbol + '\n')
        self.dispatch_event('on_completion_done', completed or command,
                            ''.join(output))

    def on_history_prev(self):
        item = self.history.previous()
        self.dispatch_event('on_history_result', item)

    def on_history_next(self):
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
