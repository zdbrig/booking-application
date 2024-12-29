import unittest
from app import app
import json

class TestRoomImageUpdater(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_update_room_images(self):
        response = self.app.post('/update-room-images')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Successfully updated all room images')

if __name__ == '__main__':
    unittest.main()
