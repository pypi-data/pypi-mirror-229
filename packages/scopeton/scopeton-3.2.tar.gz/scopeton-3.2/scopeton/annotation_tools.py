from scopeton import constants, compat


def get_annotations(instance):
    if compat.is_method(instance) or compat.is_function(instance):
        if hasattr(instance, constants.ANNOTATED):
            return getattr(instance, constants.ANNOTATED)
        return []

    return {fn: getattr(fn, constants.ANNOTATED) for fn in compat.get_methods(instance) if hasattr(fn, constants.ANNOTATED)}


def set_annotation(fn, name, value):
    if not hasattr(fn, constants.ANNOTATED):
        setattr(fn, constants.ANNOTATED, {})
    annotations = getattr(fn, constants.ANNOTATED)
    annotations[name] = value


def get_methods_with_annotation(instance, name):
    annotations = get_annotations(instance)
    return [k for k in annotations if name in annotations[k]]
