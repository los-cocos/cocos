import persistence as pe

from gamedef import game

def ingame_cls_from_combo_type(editor_type_id, ingame_type_id):
    """
    returns the class needed to intantiate in game an object whose type is
    identified by protoeditor as
    (editor_type_id, ingame_type_id)
    
    raises KeyError if combo type unknow
    version upgrades are expected to be handled not at game run time
    """
    combo_type_to_cls = {
        # (editor_type_id,   ingame_type_id): (module name, class name)
        ('levelproxy 00.01', 'level 00.01'): ("level", "Level"), 
        ('actorproxy 00.01', 'player 00.01'): ("actors", "Player"),
        ('actorproxy 00.01', 'wanderer 00.01'): ("actors", "EnemyWanderer"),
        ('actorproxy 00.01', 'chained mons 00.01'): ("actors", "EnemyChained"),
        ('actorproxy 00.01', 'tree 00.01'): ("actors", "Tree"),
        ('actorproxy 00.01', 'jewel 00.01'): ("actors", "Jewel"), 
        ('actorproxy 00.01', 'exit 00.01'): ("actors", "Exit"), 
        }
    combo_type = (editor_type_id, ingame_type_id)
    modname, clsname = combo_type_to_cls[combo_type]

    exec ("import " + modname + " as module")
    cls = getattr(module, clsname)
    return cls
        
def load_level_raw(level_filename):
    """ Reads a level saved by protoeditor as a dictionary, no interpretation
    nor checks
    """
    f = open(level_filename, 'rb')
    unpickler = pe.RestrictedUnpickler(f)
    level_dict = unpickler.load()
    f.close()
    return level_dict


def load_level(level_filename, args):
    """ Reads a level saved by protoeditor and returns a <level> instance

    args is an iterable that provides your custom positional arguments to
    use at instantiation (see in manual, sections about changing code)

    can raise KeyError if version mistmatch,
    conversions are expected to be handled not at game run time.
    """
    f = open(level_filename, 'rb')
    unpickler = pe.RestrictedUnpickler(f)
    level_dict = unpickler.load()
    f.close()
    assert 'others' in level_dict
    editor_type_id = level_dict.pop('editor_type_id')
    ingame_type_id = level_dict['ingame_type_id']
    combo_type = (editor_type_id, ingame_type_id)
    # can raise KeyError if version mistmatch
    # conversions are expected to be handled not at game run time
    assert combo_type in game['roles']['level']
    cls = ingame_cls_from_combo_type(editor_type_id, ingame_type_id)
    level = cls.new_from_dict(game, ingame_cls_from_combo_type,
                              args, level_dict)
    return level
