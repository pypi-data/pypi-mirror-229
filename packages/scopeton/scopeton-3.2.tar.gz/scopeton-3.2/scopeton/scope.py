import logging
import typing
from threading import RLock

from scopeton import compat, glob, constants, type_utils, scope_tools, annotation_tools
from scopeton.objects import Bean
from scopeton.qualifier_tree import QualifierTree
from scopeton.scope_tools import get_bean_qualifier, ScopetonException

T = typing.TypeVar("T")


class Scope(object):
    '''this is servicelocator pattern implementation'''

    def __init__(self, lock=False, parent=None):
        self._singletons = QualifierTree()
        self._beans = QualifierTree()
        self.lock = lock or RLock()  # type: RLock
        self.parent = parent  # type:  Scope
        self.servicesStarted = False
        self.children = []  # type: typing.List[Scope]
        self.registerInstance(self.__class__, self)
        if parent:
            parent.children.append(self)

    def getInstance(self, name: typing.Type[T]) -> T:
        if type_utils.is_collection(name):
            args = type_utils.get_type_args(name)
            return self.get_instances(typing.cast(typing.Type[T], args[0]))
        with self.lock:
            return self._get_instance(get_bean_qualifier(name))

    def get_instances(self, qualifier: typing.Type[T]) -> typing.List[T]:
        with self.lock:
            beans = self._beans.find_by_qualifier_name(get_bean_qualifier(qualifier))
            beans = map(lambda x: self.getInstance(x), beans)
            return list(beans)

    def _get_instance(self, qualifier):

        suitable_qualifier = self._beans.find_suitable_qualifier(qualifier)

        if self._singletons.contains(suitable_qualifier):
            return self._singletons.find_one_by_qualifier_name(suitable_qualifier)

        bean = self._beans.find_one_by_qualifier_name(suitable_qualifier)
        glob.lastScope = self

        if hasattr(bean.cls.__init__, constants.TO_INJECT_FLAG):
            # constructor injection
            instance = bean.cls()
        elif len(compat.get_method_signature(bean.cls.__init__).args) == 2:
            instance = bean.cls(self)
        elif len(compat.get_method_signature(bean.cls.__init__).args) > 2:
            raise ScopetonException(
                "Invalid number of parameters for bean constructor, maybe @Inject() decorator forgotten: {}".format(
                    compat.get_method_signature(bean.cls.__init__).args))
        else:
            instance = bean.cls()

        if bean.singleton:
            self.registerInstance(suitable_qualifier, instance)

        self._inject_injectables(instance)

        return instance

    def registerInstance(self, name, instance):
        scope_tools.set_instance_attr(instance, constants.SCOPE_PARAMETER, self)
        qualifier = get_bean_qualifier(name)
        suitableQualifier = self._beans.find_suitable_qualifier(qualifier)
        logging.debug("Suitable qualifier for {} is: {}".format(qualifier, suitableQualifier))
        self._singletons.register(suitableQualifier, instance)
        self._inject_injectables(instance)

    def registerBean(self, *args):
        with self.lock:
            for bean in args:
                if not isinstance(bean, Bean):
                    bean = Bean(bean)
                self._registerBean(bean)

    def remove(self):
        logging.debug("Removing scope: {}".format(self))
        self.stopServices()
        for k in self.children[:]:
            k.remove()
        if self.parent:
            self.parent.children.remove(self)

    def _registerBean(self, bean):
        """
        :type bean: Bean
        """
        for name in bean.qualifier_tree:
            logging.debug("Registering: {} as {}".format(name, bean))
            self._beans.register(name, bean)

    def runServices(self):
        if not self.servicesStarted:
            self.servicesStarted = True
            for bean in self._beans.get_all_objects():
                if bean.service:
                    instance = self.getInstance(bean)
                    methods = annotation_tools.get_methods_with_annotation(instance, constants.POST_CONSTRUCT)
                    for k in methods:
                        self._inject_method_args(k)

            for childScope in self.children:
                childScope.runServices()

    def stopServices(self):
        if self.servicesStarted:
            self.servicesStarted = False
            for bean in self._beans.get_all_objects():
                if bean.service:
                    methods = annotation_tools.get_methods_with_annotation(self.getInstance(bean), constants.PRE_DESTROY)
                    for k in methods:
                        self._inject_method_args(k)
            for childScope in self.children:
                childScope.stopServices()

    def _inject_injectables(self, instance):
        if hasattr(instance, constants.INJECTED):
            return
        for fn in scope_tools.get_injectables(instance):
            self._inject_method_args(fn)
        scope_tools.set_instance_attr(instance, constants.INJECTED, 1)

    def _inject_method_args(self, fn, add_self=None):
        signature = compat.get_method_signature(fn)
        nargs = []
        if add_self is not None:
            nargs.append(add_self)
        for arg_name in signature.args:
            if arg_name == "self":
                continue
            if arg_name not in signature.annotations:
                raise ScopetonException("Not annotated inject argument: {}".format(arg_name))
            nargs.append(self.getInstance(signature.annotations[arg_name]))
        return fn(*nargs)
