import unittest
import api_chatgpt as app
import json
from unittest.mock import patch, MagicMock

class AppTest(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    @patch('api_chatgpt.requests.post')
    def test_api(self, mock_post):
        # Mock request data
        mock_request = {
            "content": "Hello, world!"
        }

        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'mock-id',
            'object': 'text.completion',
            'created': 1620133500,
            'model': 'gpt-3.5-turbo',
            'choices': [
                {
                    'message': {
                        'role': 'assistant',
                        'content': 'Mocked response from OpenAI API'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Make POST request to /api endpoint
        response = self.client.post(
            '/api',
            data=json.dumps(mock_request),
            content_type='application/json',
        )

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Parse response data
        response_data = json.loads(response.data)

        # Check if 'response' key exists in response data
        self.assertIn('response', response_data)


if __name__ == "__main__":
    unittest.main()
