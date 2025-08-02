import unittest
from app.services.drive.api import DriveAPI

class TestDriveAPI(unittest.TestCase):
    def setUp(self):
        self.api = DriveAPI(account_email='test@example.com')

    def test_list_files(self):
        result = self.api.list_files()
        self.assertIsInstance(result, list)

    def test_get_file(self):
        result = self.api.get_file('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_file(self):
        result = self.api.create_file({'name': 'test.txt'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_file(self):
        result = self.api.update_file('dummy_id', {'name': 'updated.txt'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_files(self):
        result = self.api.batch_get_files(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
