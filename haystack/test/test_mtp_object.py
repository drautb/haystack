import unittest

from mtp_object import MTPObject


class TestMTPObject(unittest.TestCase):
    def setUp(self):
        self.test_model = MTPObject(42, 'file.jpg', 2, 2356)

    def test_it_should_have_an_id(self):
        self.assertEqual(self.test_model.id, 42)

    def test_it_should_have_a_name(self):
        self.assertEqual(self.test_model.name, 'file.jpg')

    def test_it_should_have_a_parent_id(self):
        self.assertEqual(self.test_model.parent_id, 2)

    def test_it_should_have_a_size(self):
        self.assertEqual(self.test_model.size, 2356)

    def test_it_should_properly_compare_objects(self):
        other = MTPObject(42, 'file.jpg', 2, 2356)
        self.assertEqual(self.test_model, other)
        self.assertTrue(self.test_model == other)
