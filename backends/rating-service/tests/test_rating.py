import unittest
from app import app
import json
from datetime import datetime

class TestRatingAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_rating(self):
        test_rating = {
            'room_id': '123',
            'guest_id': '456',
            'rating': 4,
            'comment': 'Great room!'
        }
        response = self.app.post('/ratings', 
                               data=json.dumps(test_rating),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['room_id'], '123')
        self.assertEqual(data['rating'], 4)

    def test_get_room_ratings(self):
        response = self.app.get('/ratings/room/123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_guest_ratings(self):
        response = self.app.get('/ratings/guest/456')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_room_average(self):
        response = self.app.get('/ratings/room/123/average')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('average_rating', data)

if __name__ == '__main__':
    unittest.main()
