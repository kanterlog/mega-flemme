import unittest
from app.services.docs.api import DocsAPI

class TestDocsAPI(unittest.TestCase):
    def setUp(self):
        self.api = DocsAPI(account_email='test@example.com')

    def test_get_doc(self):
        result = self.api.get_doc('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_doc(self):
        result = self.api.create_doc('Titre Test')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_doc(self):
        result = self.api.update_doc('dummy_id', [])
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_docs(self):
        result = self.api.batch_get_docs(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
