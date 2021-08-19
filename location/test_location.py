import requests_mock
from location import IPLocation
 
class TestLocation:
    def test_can_get_Latitude_and_Longitude(self):
        expected_data = {'latitude': 5, 'longitude': -23}
        with requests_mock.mock() as mock_request:
            mock_request.get('https://freegeoip.app/json/', json=expected_data)
            loc = IPLocation()
            assert loc.latitude == expected_data['latitude']
            assert loc.longitude == expected_data['longitude']
