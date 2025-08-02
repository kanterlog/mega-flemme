import unittest
from app.services.tasks.api import TasksAPI

class TestTasksAPI(unittest.TestCase):
    def setUp(self):
        self.api = TasksAPI(account_email='test@example.com')

    def test_create_task(self):
        result = self.api.create_task('dummy_list', {'title': 'Test'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_task(self):
        result = self.api.update_task('dummy_list', 'dummy_id', {'title': 'Update'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_tasks(self):
        result = self.api.batch_get_tasks('dummy_list', ['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

    def test_create_task_list(self):
        result = self.api.create_task_list({'title': 'List'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_update_task_list(self):
        result = self.api.update_task_list('dummy_list', {'title': 'Update'})
        self.assertTrue(result is None or isinstance(result, dict))

    def test_batch_get_task_lists(self):
        result = self.api.batch_get_task_lists(['dummy_id1', 'dummy_id2'])
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
