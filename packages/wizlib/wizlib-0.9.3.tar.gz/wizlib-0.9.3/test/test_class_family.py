from test.data_class_family.atriarch import Atriarch
from unittest import TestCase


class TestClassFamily(TestCase):

    def test_family_children(self):
        cx = Atriarch.family_children()
        self.assertEqual(len(cx), 1)
