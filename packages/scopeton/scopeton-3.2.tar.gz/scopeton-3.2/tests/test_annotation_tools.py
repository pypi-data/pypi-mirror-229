import unittest

from scopeton import annotation_tools


class Dependency(object):
    def test(self):
        pass

    def testDecorated(self, param):
        pass


class AnnotationToolsTest(unittest.TestCase):

    def test_set_annotations(self):
        annotation_tools.set_annotation(Dependency.test, "test_annotation", 1)
        annotated_methods = annotation_tools.get_methods_with_annotation(Dependency(), "test_annotation")
        self.assertEqual(annotated_methods[0].__func__, Dependency.test)

    def test_get_annotations(self):
        annotation_tools.set_annotation(Dependency.test, "test_annotation", 1)
        annotated_methods = annotation_tools.get_annotations(Dependency.test)
        self.assertEqual(annotated_methods, {"test_annotation": 1})
        annotated_methods = annotation_tools.get_annotations(Dependency().test)
        self.assertEqual(annotated_methods, {"test_annotation": 1})
