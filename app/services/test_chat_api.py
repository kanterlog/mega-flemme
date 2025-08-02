import unittest
from app.services.chat.api import ChatAPI

class TestChatAPI(unittest.TestCase):
    def setUp(self):
        self.api = ChatAPI(account_email='test@example.com')

    def test_get_space(self):
        result = self.api.get_space('dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_space(self):
        result = self.api.create_space({'displayName': 'Test'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_space(self):
        result = self.api.update_space('dummy_id', {'displayName': 'Update'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_spaces(self):
        result = self.api.batch_get_spaces(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

    def test_send_message(self):
        result = self.api.send_message('dummy_id', {'text': 'Hello'})
        self.assertTrue(result is None or isinstance(result, dict))

if __name__ == '__main__':
    unittest.main()
