import unittest
from app.services.sheets.api import SheetsAPI

class TestSheetsAPI(unittest.TestCase):
    def setUp(self):
        self.api = SheetsAPI(account_email='test@example.com')

    def test_get_spreadsheet(self):
        result = self.api.get_spreadsheet('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_spreadsheet(self):
        result = self.api.create_spreadsheet({'properties': {'title': 'Test'}})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_spreadsheet(self):
        result = self.api.update_spreadsheet('dummy_id', [])
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_spreadsheets(self):
        result = self.api.batch_get_spreadsheets(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
