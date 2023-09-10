from scopeton import compat, constants


def flatten(lst):
    res = []
    for el in lst:
        if type(el) is list:
            res += flatten(el)
        else:
            res.append(el)
    return res


def get_class_name(cls):
    return cls.__name__ if hasattr(cls, "__name__") else str(cls)


def get_class_tree_qualifiers(cls):
    res = [get_bean_qualifier(k) for k in get_class_tree(cls)]
    res.reverse()
    return res


def rm_dups(lst):
    res = []
    for k in lst:
        if k not in res:
            res.append(k)
    return res


def get_class_tree(cls):
    return rm_dups(_get_class_tree(cls))


def _get_class_tree(cls):
    res = [cls]
    if type(cls) is not object and hasattr(cls, "__bases__") and cls.__bases__:
        res += flatten([_get_class_tree(parent) for parent in cls.__bases__])
    return res


def get_bean_qualifier(bean) -> str:
    if isinstance(bean, str):
        return bean
    from scopeton.objects import Bean
    if isinstance(bean, Bean):
        return bean.qualifier_tree[-1]
    if not hasattr(bean, "__name__"):
        return str(bean)
    return bean.__name__


def call_method_by_name(obj, name, *args, **kwargs):
    if hasattr(obj, name):
        return getattr(obj, name)(*args, **kwargs)


def get_injectables(instance):
    return [fn for fn in compat.get_methods(instance) if hasattr(fn, constants.TO_INJECT_FLAG)]


def get_scope_by_method_or_class(target):
    if compat.is_method(target):
        target = compat.get_method_instance(target)
    if not hasattr(target, constants.SCOPE_PARAMETER):
        raise ScopetonException("No scope parameter: {} for instance {}".format(constants.SCOPE_PARAMETER, target))
    return getattr(target, constants.SCOPE_PARAMETER)


class ScopetonException(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)


def set_instance_attr(instance, attr, value):
    if is_primitive(instance):
        return
    setattr(instance, attr, value)


def is_primitive(obj):
    return not hasattr(obj, '__dict__')
