import unittest
from app.services.calendar_api.api import CalendarAPI

class TestCalendarAPI(unittest.TestCase):
    def setUp(self):
        self.api = CalendarAPI(account_email='test@example.com')

    def test_list_events(self):
        result = self.api.list_events()
        self.assertIsInstance(result, list)

    def test_get_event(self):
        result = self.api.get_event('primary', 'dummy_id')
        self.assertTrue(result is None or isinstance(result, dict))

    def test_create_event(self):
        result = self.api.create_event('primary', {'summary': 'Test'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_event(self):
        result = self.api.update_event('primary', 'dummy_id', {'summary': 'Update'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_events(self):
        result = self.api.batch_get_events('primary', ['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
