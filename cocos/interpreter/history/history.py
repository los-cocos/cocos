import collections
import os.path


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
