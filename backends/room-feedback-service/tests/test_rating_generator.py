import unittest
from unittest.mock import patch, MagicMock
import json
from app import app

class TestRatingGenerator(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('requests.get')
    @patch('requests.post')
    def test_rating_generation(self, mock_post, mock_get):
        # Mock room response
        mock_room_response = [{"id": "room_123"}]
        mock_get.return_value.json.return_value = mock_room_response
        mock_get.return_value.status_code = 200
        
        # Mock rating post response
        mock_post.return_value.status_code = 201

        # Test start endpoint
        response = self.app.post('/generator/start')
        self.assertEqual(response.status_code, 200)
        
        # Verify response format
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Rating generation started')

if __name__ == '__main__':
    unittest.main()

