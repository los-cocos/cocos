import readline

from history import History


class ReadlineHistory(History):
    def __len__(self):
        return readline.get_current_history_length()

    def load(self, filename, size):
        readline.read_history_file(filename)
        readline.set_history_length(size)

    def save(self):
        if self.filename:
            readline.write_history_file(self.filename)

    def reset(self, size):
        readline.set_history_length(size)

    def append(self, item):
        if len(item):
            readline.add_history(item)
            self._update_index()

    def next(self):
        item = ''
        history_length = readline.get_current_history_length()
        self.index += 1
        if self.index <= history_length:
            item = readline.get_history_item(self.index)
        else:
            self.index = history_length+1
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
        self.index = readline.get_current_history_length()+1

