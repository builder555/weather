import pytest
import requests_mock
from unittest.mock import MagicMock, patch
from weatherapi import Weather
 
class TestWeather:
    def test_can_get_expected_precipitation(self, fake_location):
        w = Weather(fake_location)
        assert w.precipitation == 1.2

    def test_can_get_temperature(self, fake_location):
        w = Weather(fake_location)
        assert w.temperature == 15

    def test_request_updated_weather_every_X_minutes(self, fake_location, fake_timer):
        with patch('weatherapi.main.requests') as mock_request:
            w = Weather(fake_location, update_frequency=10)
            assert mock_request.get.call_count == 1
            fake_timer.forward(seconds=10*60)
            assert mock_request.get.call_count == 2
    
    def test_when_setting_publisher_must_set_at_least_one_argument(self, weather):
        with pytest.raises(Exception):
            weather.set_publisher(MagicMock())

    def test_publish_1_when_desired_temperature_and_precipitation_reached(self, weather, set_temperature, set_precipitation):
        mock_publisher = MagicMock()
        set_precipitation(1)
        set_temperature(15)
        weather.set_publisher(mock_publisher, below_precipitation=2, above_temperature=10)
        mock_publisher.publish.assert_called_with('1')
        weather.set_publisher(mock_publisher, above_precipitation=0, below_temperature=20)
        mock_publisher.publish.assert_called_with('1')

    def test_publish_0_when_desired_temperature_or_precipitation_not_reached(self, weather, set_temperature, set_precipitation):
        mock_publisher = MagicMock()
        set_precipitation(2)
        set_temperature(15)
        weather.set_publisher(mock_publisher, below_precipitation=2, above_temperature=10)
        mock_publisher.publish.assert_called_with('0')
        weather.set_publisher(mock_publisher, below_precipitation=5, above_temperature=15)
        mock_publisher.publish.assert_called_with('0')

    def test_publish_1_when_desired_temperature_is_within_range(self, weather, set_temperature, set_precipitation):
        mock_publisher = MagicMock()
        set_temperature(10)
        weather.set_publisher(mock_publisher, above_temperature=5, below_temperature=15)
        mock_publisher.publish.assert_called_with('1')

    def test_publish_0_when_desired_temperature_is_outside_of_range(self, weather, set_temperature, set_precipitation):
        mock_publisher = MagicMock()
        set_temperature(10)
        weather.set_publisher(mock_publisher, above_temperature=15, below_temperature=25)
        mock_publisher.publish.assert_called_with('0')
        weather.set_publisher(mock_publisher, above_temperature=5, below_temperature=10)
        mock_publisher.publish.assert_called_with('0')

    def test_publish_1_when_desired_precipitation_is_within_range(self, weather, set_precipitation):
        mock_publisher = MagicMock()
        set_precipitation(2)
        weather.set_publisher(mock_publisher, above_precipitation=1, below_precipitation=3)
        mock_publisher.publish.assert_called_with('1')

    def test_publish_0_when_desired_precipitation_is_outside_of_range(self, weather, set_precipitation):
        mock_publisher = MagicMock()
        set_precipitation(2)
        weather.set_publisher(mock_publisher, above_precipitation=0, below_precipitation=2)
        mock_publisher.publish.assert_called_with('0')
        weather.set_publisher(mock_publisher, above_precipitation=2, below_precipitation=4)
        mock_publisher.publish.assert_called_with('0')

@pytest.fixture(autouse=True)
def mock_request(fake_location, fake_weather_data):
    lat,lon = fake_location.latitude, fake_location.longitude
    url = f'https://api.met.no/weatherapi/locationforecast/2.0/compact.json?lat={lat}&lon={lon}'
    with requests_mock.mock() as m:
        m.get(url, json=fake_weather_data)
        yield m

@pytest.fixture
def weather(fake_location):
    return Weather(fake_location)

@pytest.fixture
def fake_location():
    lat = 5
    lon = -23
    return MagicMock(latitude=lat, longitude=lon)

@pytest.fixture(autouse=True)
def fake_timer():
    class FakeTimer:
        def __new__(cls, interval=0, function=lambda: None):
            cls.interval = interval
            cls.callback = function
            cls.__is_running = False
            return super(FakeTimer, cls).__new__(cls)
        @classmethod
        def start(cls):
            cls.__is_running = True
        @classmethod
        def cancel(cls):
            cls.__is_running = False
        @classmethod
        def forward(cls, seconds):
            if not cls.__is_running:
                raise Exception('Timer has to be running')
            while seconds >= cls.interval:
                cls.callback()
                seconds -= cls.interval
    with patch('weatherapi.main.Timer', new=FakeTimer):
        yield FakeTimer

@pytest.fixture
def fake_weather_data():
    return {
        "properties": {
            "timeseries": [
                {
                    "time": "2021-08-17T11:00:00Z",
                    "data": {
                        "instant": {
                            "details": {
                                "air_pressure_at_sea_level": 1017.9,
                                "air_temperature": 15,
                                "cloud_area_fraction": 88.3,
                                "relative_humidity": 97.8,
                                "wind_from_direction": 50.1,
                                "wind_speed": 2
                            }
                        },
                        "next_12_hours": {
                            "summary": {
                                "symbol_code": "lightrainshowers_day"
                            }
                        },
                        "next_1_hours": {
                            "summary": {
                                "symbol_code": "partlycloudy_day"
                            },
                            "details": {
                                "precipitation_amount": 1.2
                            }
                        },
                        "next_6_hours": {
                            "summary": {
                                "symbol_code": "lightrainshowers_day"
                            }
                        }
                    }
                }
            ]
        }
    }

@pytest.fixture
def set_temperature(fake_weather_data):
    def setter(temp):
        fake_weather_data['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']=temp
    return setter

@pytest.fixture
def set_precipitation(fake_weather_data):
    def setter(temp):
        fake_weather_data['properties']['timeseries'][0]['data']['next_1_hours']['details']['precipitation_amount']=temp
    return setter
