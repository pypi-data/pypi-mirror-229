import inspect
import sys


class _Python2NativeArgs:
    args = ['self']


def is_python3():
    return sys.version_info.major >= 3


def get_methods(instance):
    return [k[1] for k in inspect.getmembers(instance, predicate=inspect.ismethod)]


def get_method_instance(method):
    if not hasattr(method, "__self__"):
        return None
    return method.__self__


def is_class(obj):
    if not is_python3():
        import new
        return type(obj) is new.classobj or type(obj) is type
    else:
        import inspect
        return inspect.isclass(obj)


def object_is_instance(obj):
    if not is_python3():
        import new
        return type(obj) is new.instance or (hasattr(obj, "__class__") and hasattr(obj.__class__, "__name__"))
    else:
        import inspect
        return inspect.isclass(obj)


def get_method_signature(method):
    if is_python3():
        return inspect.getfullargspec(method)
    else:
        try:
            return inspect.getargspec(method)
        except TypeError:
            return _Python2NativeArgs()


def is_method(fn):
    return inspect.ismethod(fn)
def is_function(fn):
    return inspect.isfunction(fn)