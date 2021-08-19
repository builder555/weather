import requests
from threading import Timer

class Weather:
    def __init__(self, location, update_frequency=30):
        self.__period = update_frequency
        self.__lat = location.latitude
        self.__lon = location.longitude
        self.__publisher = None
        self.__update()
        self.__timer = Timer(self.__period * 60, self.__update)
        self.__timer.start()

    def set_publisher(self, publisher, below_temperature=None, above_temperature=None,
                                below_precipitation=None, above_precipitation=None):
        self.__low_t = below_temperature
        self.__low_p = below_precipitation
        self.__high_t = above_temperature
        self.__high_p = above_precipitation
        assert ( below_temperature is not None or
                below_precipitation is not None or
                above_temperature is not None or
                above_precipitation is not None)
        self.__publisher = publisher
        self.__update()

    def __update(self):
        url = "https://api.met.no/weatherapi/locationforecast/2.0/" +\
            f"compact.json?lat={self.__lat}&lon={self.__lon}"
        resp = requests.get(url, headers={'User-Agent': 'Weather Block'})
        self.__weather_data = resp.json()
        if self.__publisher:
            result = (
                    (self.__low_t is None or self.__low_temp_ok) and
                    (self.__high_t is None or self.__high_temp_ok) and
                    (self.__low_p is None or self.__low_precip_ok) and
                    (self.__high_p is None or self.__high_precip_ok)
                )
            self.__publisher.publish(str(int(result)))
        self.__timer = Timer(self.__period * 60, self.__update)
        self.__timer.start()

    @property
    def __low_temp_ok(self):
        return self.temperature < self.__low_t
    @property
    def __high_temp_ok(self):
        return self.temperature > self.__high_t
    @property
    def __low_precip_ok(self):
        return self.precipitation < self.__low_p
    @property
    def __high_precip_ok(self):
        return self.precipitation > self.__high_p

    @property
    def precipitation(self):
        time_series = self.__weather_data.get('properties', {}).get('timeseries', [])
        precipitation = 0
        if time_series:
            forecast = time_series[0].get('data', {}).values()
            for time_range in forecast:
                precipitation += time_range.get('details', {}).get('precipitation_amount', 0)
        return precipitation

    @property
    def temperature(self):
        time_series = self.__weather_data.get('properties', {}).get('timeseries', [])
        temperature = 0
        if time_series:
            forecast = time_series[0].get('data', {}).values()
            for time_range in forecast:
                latest_temperature = time_range.get('details', {}).get('air_temperature', None)
                if latest_temperature is not None:
                    temperature = latest_temperature
        return temperature

    def __del__(self):
        self.__timer.cancel()
