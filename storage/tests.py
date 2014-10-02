from django.test import TestCase
from .models import Storage


class StorageTestCase(TestCase):
    def setUp(self):
        pass

    def test_make_path(self):
        class Obj(object):
            def __init__(self, pk):
                self.pk = pk

        obj = Obj(123)
        self.assertEqual(u'st1/23/01/000000.jpg', Storage.make_path(obj, 'abra.jpg'))
