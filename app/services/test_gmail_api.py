import unittest
from app.services.gmail.api import GmailAPI

class TestGmailAPI(unittest.TestCase):
    def setUp(self):
        # Remplacer par un email de test ou mock
        self.api = GmailAPI(account_email='test@example.com')

    def test_list_messages(self):
        result = self.api.list_messages()
        self.assertIsInstance(result, list)

    def test_get_message(self):
        # Utiliser un ID de message de test ou mock
        result = self.api.get_message('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_send_message(self):
        # Utiliser un message RFC822 base64 de test ou mock
        result = self.api.send_message('dGVzdA==')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_draft(self):
        result = self.api.create_draft('dGVzdA==')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_messages(self):
        result = self.api.batch_get_messages(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
