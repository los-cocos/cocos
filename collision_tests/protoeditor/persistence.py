import pickle
import struct
import types
class RestrictedPickler(pickle.Pickler):
    """
    A pickler that will reject 'too complex' parts.
    It allows None, bool, int, strings, float, tuple, list, dict
    And allows nesting.
    The plausible use cases only need to reject instances of custom classes.
    """
    dispatch = dict(pickle.Pickler.dispatch)
    def save_global(self, obj, name=None, pack=struct.pack):
        raise TypeError
    dispatch[types.ClassType] = save_global
    dispatch[types.FunctionType] = save_global
    dispatch[types.BuiltinFunctionType] = save_global
    dispatch[types.TypeType] = save_global

class RestrictedUnpickler(pickle.Unpickler):
    """
    Unpickler that will reject too complex parts.
    It allows None, bool, int, strings, float, tuple, list, dict
    And allows nesting.
    The plausible use cases only need to reject instances of custom classes.
    """
    def _instantiate(self, klass, k):
        raise TypeError
    def load_global(self):
        raise TypeError
    
