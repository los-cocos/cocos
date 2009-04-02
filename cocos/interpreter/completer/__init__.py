
try:
    import rlcompleter
    has_readline = True
except:
    has_readline = False

from completer import Completer

if has_readline:
    from _readline import ReadlineCompleter
