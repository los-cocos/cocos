import traceback

from pyglet.window import key

from console import Console, Interpreter
from plugin import Plugin, Mode, EventHandler


DEADGRAVE = 210453397504

class EditorConsole(Console):
    def __init__(self, editor):
        self.locals = {}
        super(EditorConsole, self).__init__(self.locals)
        self.editor = editor
        self.mode_vars = {}
        self.vars = {}
        self.mode_cmds = {}
        self.cmds = {}
        self.add_command('help', self.do_help)
        
    def add_mode_variable(self, mode, varname, getter):
        self.mode_vars.setdefault(mode, {})[varname] = getter
    
    def add_variable(self, varname, getter):
        self.vars[varname] = getter

    def add_mode_command(self, mode, cmd, callable):
        self.mode_cmds.setdefault(mode, {})[varname] = getter
    
    def add_command(self, cmd, callable):
        self.cmds[cmd] = callable
    
    def do_layers(self, rest):
        for n, l in self.ed.layers.children_names.items():
            label = getattr(l, "label", None)
            if label is None:
                label = "<unlabelled>"
            self._write("%s: %s\n" % (n, label))

    def do_help(self, rest):
        def write_section(name, source):
            self._write(name + "\n")
            for k, v in source.items():
                if v.__doc__ is not None:
                    self._write("%s: %s\n" % (k, v.__doc__))
                else:
                    self._write(k + "\n")
            self._write("\n")
        mode = self.editor.current_mode.name            
        write_section("Variables", self.vars)
        if mode in self.mode_vars:
            write_section("Mode Variables", self.mode_vars[mode])                    
        write_section("Commands", self.cmds)
        if mode in self.mode_cmds:
            write_section("Mode Commands", self.mode_cmds[mode])                    
            
            
    def calculate_variables(self, source):
        for k, v in source.items():
            try:
                r = v()
            except:
                traceback.print_exc()
                if k in self.locals:
                    del self.locals[k]
            else:
                self.locals[k] = r
                
    def evaluate(self, input, first=True):
        mode = self.editor.current_mode.name
        self.calculate_variables(self.vars)
        if mode in self.mode_vars:
            self.calculate_variables(self.mode_vars[mode])
        
        if first:
            parts = input.split(" ")
            if parts:
                start = parts[0].strip()
                rest = " ".join(parts[1:])
                if start in self.cmds:
                    self.cmds[start](rest)
                    return
                
                elif mode in self.mode_cmds and start in self.mode_cmds[mode]:
                    self.mode_cmds[mode][start](rest)
                    return
                
        return super(EditorConsole, self).evaluate(input, first)


class ConsoleEventHandler(EventHandler):

    def __init__(self, editor, console):
        self.editor = editor
        self.console = console
        self.console_visible = None
        self.mouse_position = 0,0
        
    def toggle_console(self):
        if not self.console_visible:
            self.editor.add(self.console, z=100)
        else:
            self.editor.remove(self.console)
        self.console_visible = not self.console_visible
        
    def on_key_press(self, k, m):
        print k

        if k == key.F12:
            self.toggle_console()
            return True

    def on_mouse_drag(self, px, py, dx, dy, b, m):
        self.mouse_position = px, py
        
    def on_mouse_motion(self, px, py, dx, dy):
        self.mouse_position = px, py
        
        
    

class ConsolePlugin(Plugin):
    name = 'console'
    def __init__(self, editor):
        self.editor = editor
        console = EditorConsole(editor)
        self.editor.console = console
        self.handler = ConsoleEventHandler(editor, console)
        self.editor.register_handler(self.handler)
        
        def get_editor():
            'the editor instance'
            return editor
        
        
        console.add_variable('editor', get_editor)
        bookmarks = {}
        def goto(name):
            'goto bookmark NAME'
            try:
                self.editor.look_at(*bookmarks[name])
            except KeyError:
                pass
        editor.console.add_command('goto', goto)
        def mark(name):
            'mark this location as NAME'
            bookmarks[name] = self.editor.layers.pointer_to_world(
                *self.handler.mouse_position)
        editor.console.add_command('mark', mark)
    
    