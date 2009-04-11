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
'''A readline based History management class for the python interpreter

ReadlineHistory
===============

TBD

'''

__docformat__ = 'restructuredtext'

import readline

from history import History


class ReadlineHistory(History):
    def __len__(self):
        return readline.get_current_history_length()

    def load(self, filename, size):
        readline.read_history_file(filename)
        readline.set_history_length(size)

    def save(self):
        if self.persistent and self.filename:
            readline.write_history_file(self.filename)

    def reset(self, size):
        readline.set_history_length(size)

    def append(self, item):
        if item:
            readline.add_history(item)
            self._update_index()

    def next(self):
        item = ''
        history_length = readline.get_current_history_length()
        self.index += 1
        if self.index <= history_length:
            item = readline.get_history_item(self.index)
        else:
            self.index = history_length + 1
        return item

    def previous(self):
        item = ''
        self.index -= 1
        if self.index > 0:
            item = readline.get_history_item(self.index)
        else:
            self.index = 0
        return item

    def _update_index(self):
        self.index = readline.get_current_history_length() + 1

