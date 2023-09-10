from scopeton import glob, constants, annotation_tools


def Inject():
    def inject_decorator(fn):
        if fn.__name__ == '__init__':
            # constructor injector
            def inject_wrapper(*args, **kwags):
                return glob.lastScope._inject_method_args(fn, args[0])
        else:
            inject_wrapper = fn

        setattr(inject_wrapper, constants.TO_INJECT_FLAG, 1)
        return inject_wrapper

    return inject_decorator


def PostConstruct():
    def post_construct_decorator(fn):
        annotation_tools.set_annotation(fn, constants.POST_CONSTRUCT, 1)
        return fn

    return post_construct_decorator

def PreDestroy():
    def pre_destroy_decorator(fn):
        annotation_tools.set_annotation(fn, constants.PRE_DESTROY, 1)
        return fn

    return pre_destroy_decorator
