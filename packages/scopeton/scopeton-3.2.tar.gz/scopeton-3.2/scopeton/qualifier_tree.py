import logging
import typing
from threading import RLock

from scopeton.scope_tools import ScopetonException, flatten


class QualifierTree:
    def __init__(self):
        self._qualifiers = {}  # type: dict[str, typing.List[object]]
        self._qualifiersMap = {}  # type: dict[object, typing.List[str]]
        self.lock = RLock()

    def _register_obj(self, qualifier_name: str, obj):
        with self.lock:
            self._reg_object_by_qualifier(qualifier_name, obj)
            self._reg_qualifier_by_object(qualifier_name, obj)

    def _reg_object_by_qualifier(self, qualifier_name, obj):
        if qualifier_name not in self._qualifiers:
            self._qualifiers[qualifier_name] = []
        if obj not in self._qualifiers[qualifier_name]:
            logging.debug("Registering: {}".format(obj))
            self._qualifiers[qualifier_name].append(obj)

    def _reg_qualifier_by_object(self, qualifier_name, obj):
        if obj not in self._qualifiersMap:
            self._qualifiersMap[obj] = []
        if qualifier_name not in self._qualifiersMap[obj]:
            self._qualifiersMap[obj].append(qualifier_name)

    def register(self, names: typing.Union[typing.List[str], str], obj):
        if isinstance(names, str):
            names = [names]
        for name in names:
            self._register_obj(name, obj)

    def find_qualifiers(self, obj):
        return self._qualifiersMap[obj]

    def check_object_has_qualifier(self, qualifier, object):
        return qualifier in self._qualifiersMap[object]

    def get_qualifier_tree_length(self, obj):
        return len(self.find_qualifiers(obj))

    def find_suitable_qualifier(self, qualifier):
        if qualifier not in self._qualifiers:
            return qualifier
        objects = self._qualifiers[qualifier]
        if len(objects) > 1:
            raise Exception("expected 1 object for qualifier:{}, but got {}: {}".format(qualifier, len(objects), objects))
        if len(objects) == 0:
            raise Exception("No objects for qualifier:{}".format(qualifier))
        return self.find_qualifiers(objects[0])[-1]

    def contains(self, name):
        return name in self._qualifiers

    def get_all_objects(self):
        lists = flatten([self._qualifiers[q] for q in self._qualifiers])
        return list(set(lists))

    def find_by_qualifier_name(self, name):
        with self.lock:
            if name not in self._qualifiers:
                return []
            return self._qualifiers[name]

    def find_one_by_qualifier_name(self, name):
        with self.lock:
            beans = self.find_by_qualifier_name(name)
            if len(beans) == 0:
                raise ScopetonException("Error, no such qualifier: {}".format(name))
            if len(beans) > 1:
                raise ScopetonException("{} qualifier for name: {}, expected 1, objects: {}".format(len(self._qualifiers[name]), name, self._qualifiers[name]))

            return beans[0]
