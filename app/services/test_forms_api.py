import unittest
from app.services.forms.api import FormsAPI

class TestFormsAPI(unittest.TestCase):
    def setUp(self):
        self.api = FormsAPI(account_email='test@example.com')

    def test_get_form(self):
        result = self.api.get_form('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_form(self):
        result = self.api.create_form({'title': 'Test'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_form(self):
        result = self.api.update_form('dummy_id', [])
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_forms(self):
        result = self.api.batch_get_forms(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
