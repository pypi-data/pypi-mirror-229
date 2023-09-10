import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pyholaclient

class TestHolaClient(unittest.TestCase):
    def test_init(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        self.assertEqual(client.api_url, 'http://localhost')
        self.assertEqual(client.api_key, '123')
        # Print status of the test
        print('TestHolaClient.test_init: OK')
    def test_user(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        user = client.user_info('example@gmail.com')
        self.assertEqual(user.email, 'example@gmail.com')
        print('TestHolaClient.test_user Email: OK')
        self.assertEqual(user.first_name, 'CR072')
        print('TestHolaClient.test_user First Name: OK')
        self.assertEqual(user.last_name, 'discord-auth')
        print('TestHolaClient.test_user Last Name: OK')
        self.assertEqual(user.username, 'crazymath072')
        print('TestHolaClient.test_user Username: OK')
        self.assertEqual(user.language, 'en')
        print('TestHolaClient.test_user Language: OK')
        self.assertEqual(user.id, 2)
        print('TestHolaClient.test_user ID: OK')
        self.assertEqual(user.external_id, None)
        print('TestHolaClient.test_user External ID: OK')
        self.assertEqual(user.root_admin, True)
        print('TestHolaClient.test_user Root Admin: OK')
        self.assertEqual(user.twofa_enabled, False)
        print('TestHolaClient.test_user 2FA: OK')
        self.assertEqual(user.uuid, '365153fc-xxx-xxx-xxx-xxxx')
        print('TestHolaClient.test_user UUID: OK')
        self.assertEqual(user.created_at, '2023-07-21T14:51:13+00:00')
        print('TestHolaClient.test_user Created At: OK')
        self.assertEqual(user.updated_at, '2023-07-28T08:46:27+00:00')
        print('TestHolaClient.test_user Updated At: OK')
        self.assertEqual(user.relationships, {})
        print('TestHolaClient.test_user Relationships: OK')



if __name__ == '__main__':
    unittest.main()
