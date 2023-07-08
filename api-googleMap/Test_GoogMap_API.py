import unittest
from unittest.mock import patch
from GoogMap_API import app


class TestSearchDoctors(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    @patch('GoogMap_API.Nominatim')
    @patch('GoogMap_API.GoogleSearch')
    def test_search_doctors_success(self, mock_google_search, mock_geolocator):
        # Mock Nominatim geolocation
        mock_geolocator().geocode.return_value.latitude = 40.7455096
        mock_geolocator().geocode.return_value.longitude = -74.0083012

        # Mock GoogleSearch results
        mock_results = {
            'local_results': [
                {'title': 'Doctor 1', 'address': 'Address 1'},
                {'title': 'Doctor 2', 'address': 'Address 2'}
            ]
        }
        mock_google_search().get_dict.return_value = mock_results

        # Send a test request
        response = self.app.get('/search?doctorType=dentist&address=New+York')

        # Verify the response
        self.assertEqual(response.status_code, 200)
        expected_result = {
            'dentist': [
                {'name': 'Doctor 1', 'address': 'Address 1'},
                {'name': 'Doctor 2', 'address': 'Address 2'}
            ]
        }
        self.assertEqual(response.get_json(), expected_result)

    def test_search_doctors_missing_params(self):
        # Send a test request with missing parameters
        response = self.app.get('/search')

        # Verify the response
        self.assertEqual(response.status_code, 400)
        expected_result = {'error': 'Missing required parameters.'}
        self.assertEqual(response.get_json(), expected_result)

    @patch('GoogMap_API.Nominatim')
    def test_search_doctors_geocoding_failure(self, mock_geolocator):
        # Mock Nominatim geolocation to return None
        mock_geolocator().geocode.return_value = None

        # Send a test request with a valid doctorType but invalid address
        response = self.app.get('/search?doctorType=dentist&address=Invalid+Address')

        # Verify the response
        self.assertEqual(response.status_code, 400)
        expected_result = {'error': 'Geocoding failed. Invalid address or API error.'}
        self.assertEqual(response.get_json(), expected_result)

    @patch('GoogMap_API.Nominatim')
    @patch('GoogMap_API.GoogleSearch')
    def test_search_doctors_no_results(self, mock_google_search, mock_geolocator):
        # Mock Nominatim geolocation
        mock_geolocator().geocode.return_value.latitude = 40.7455096
        mock_geolocator().geocode.return_value.longitude = -74.0083012

        # Mock GoogleSearch to return no results
        mock_results = {'local_results': []}
        mock_google_search().get_dict.return_value = mock_results

        # Send a test request with valid parameters but no search results
        response = self.app.get('/search?doctorType=dentist&address=New+York')

        # Verify the response
        self.assertEqual(response.status_code, 200)
        expected_result = {'dentist': []}
        self.assertEqual(response.get_json(), expected_result)


if __name__ == '__main__':
    unittest.main()
