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
'''A base autocompleter for the python interpreter

Completer
=========

TBD

'''

__docformat__ = 'restructuredtext'

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
        text = split_line[-1]
        state = 0
        completion = self._get_completion(text, state)
        while completion:
            possibilities.append(completion)
            state += 1
            completion = self._get_completion(text, state)
        if possibilities:
            common_prefix = os.path.commonprefix(possibilities)
            completed = line[:-len(text)] + common_prefix
        else:
            completed = line
        return completed, possibilities

    def _get_completion(self, text, state):
        matches = sorted(self._get_matches(text))
        if len(matches) > state:
            return matches[state]

    def _get_matches(self, text):
        matches = set()
        for target in self._namespace:
            if target.startswith(text):
                matches.add(target)
        return matches

    @apply
    def namespace():
        def fget(self):
            return self._namespace
        def fset(self, value):
            self._namespace = value
        return property(fget, fset)

