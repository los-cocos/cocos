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
'''A base History management class for the python interpreter

History
=======

TBD

'''

__docformat__ = 'restructuredtext'

import collections
import os.path
import pickle


class History(object):

    def __init__(self, filename=None, size=100, persistent=False):
        self.filename = filename
        self.size = size
        self.persistent = persistent
        if filename and os.path.exists(filename):
            self.load(filename, size)
        else:
            self.reset(size)
        self._update_index()

    def __len__(self):
        return len(self.data)

    def __del__(self):
        self.persist()

    def load(self, filename, size):
        self.data = pickle.load(open(filename, 'rb'))

    def persist(self):
        if self.persistent and self.filename:
            pickle.dump(self.data, open(self.filename, 'wb'))

    def reset(self, size):
        self.data = collections.deque([''])

    def append(self, item):
        if len(item):
            self.data.append(item)
            if len(self.data) > self.size:
                self.data.popleft()
            self._update_index()

    def next(self):
        item = ''
        history_length = len(self.data)
        self.index += 1
        if self.index < history_length:
            item = self.data[self.index]
        else:
            self.index = history_length
        return item

    def previous(self):
        item = ''
        if self.index > 0:
            self.index -= 1
            item = self.data[self.index]
        else:
            self.index = 0
        return item

    def _update_index(self):
        self.index = len(self.data)
