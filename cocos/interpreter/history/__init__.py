
try:
    import readline
    has_readline = True
except:
    has_readline = False

from history import History

if has_readline:
    from _readline import ReadlineHistory
